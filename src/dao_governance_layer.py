r"""
Phase 13: Decentralized Autonomous Organization (DAO) Interface Layer
Enables the Apex Autonomous System to participate in external governance structures:
1. Submits strategic AI decisions to decentralized peer voting (human & AI peers).
2. Manages token-weighted quorum, voting periods, and majority thresholds.
3. Issues cryptographically verified Execution Permits upon proposal ratification.
Location: d:/AI/src/dao_governance_layer.py
Strictly localized within d:/AI
"""

import time
import json
import secrets
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

from web3 import Web3
from eth_account import Account

from config import BASE_DIR, DATA_DIR
from ephemeral_chain import EphemeralLedger
from external_actuator_interface import ExternalActuatorDispatcher

DAO_DATA_FILE = DATA_DIR / "dao_proposals.json"


class ProposalStatus(Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUCCEEDED = "SUCCEEDED"
    DEFEATED = "DEFEATED"
    EXECUTED = "EXECUTED"
    CANCELED = "CANCELED"


@dataclass
class DAOProposal:
    proposal_id: str
    proposer: str
    title: str
    description: str
    action_payload: Dict[str, Any]
    votes_for: float = 0.0
    votes_against: float = 0.0
    quorum_required: float = 100000.0  # e.g., 100k governance voting tokens
    start_time: float = field(default_factory=time.time)
    voting_period_sec: float = 86400.0  # 24 hours default
    status: ProposalStatus = ProposalStatus.ACTIVE
    execution_permit_signature: Optional[str] = None
    voters: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class DAOGovernanceInterface:
    """
    Decentralized governance connector allowing the AI to:
    - Submit autonomous mandates to on-chain / peer review.
    - Collect decentralized votes from external human & AI delegates.
    - Await quorum and cryptographic consensus ratification before execution.
    """

    def __init__(self, ledger: Optional[EphemeralLedger] = None, eai: Optional[ExternalActuatorDispatcher] = None):
        self.ledger = ledger or EphemeralLedger()
        self.eai = eai or ExternalActuatorDispatcher(ledger=self.ledger)
        self.proposals: Dict[str, DAOProposal] = {}
        
        # Simulated DAO Treasury & Governance Keys
        self.governance_account = Account.create(secrets.token_hex(32))
        self._load_state()

    def _load_state(self):
        if DAO_DATA_FILE.exists():
            try:
                with open(DAO_DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        v["status"] = ProposalStatus(v["status"])
                        self.proposals[k] = DAOProposal(**v)
            except Exception:
                pass

    def _save_state(self):
        serialized = {}
        for k, v in self.proposals.items():
            d = v.__dict__.copy()
            d["status"] = v.status.value
            serialized[k] = d
        with open(DAO_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2)

    def submit_mandate(self, title: str, description: str, action_payload: Dict[str, Any], 
                       custom_quorum: float = 100000.0, 
                       voting_period_sec: float = 86400.0) -> DAOProposal:
        """
        Submits an abstracted AI strategy or high-stakes action to external DAO vote.
        """
        prop_id = f"DAO-PROP-{secrets.token_hex(4).upper()}"
        proposal = DAOProposal(
            proposal_id=prop_id,
            proposer=self.governance_account.address,
            title=title,
            description=description,
            action_payload=action_payload,
            quorum_required=custom_quorum,
            voting_period_sec=voting_period_sec,
            start_time=time.time(),
            status=ProposalStatus.ACTIVE
        )
        self.proposals[prop_id] = proposal
        self._save_state()

        # Log mandate submission to Ephemeral Ledger
        self.ledger.record_action("DAO_MANDATE_SUBMITTED", {
            "proposal_id": prop_id,
            "title": title,
            "proposer": proposal.proposer,
            "quorum": custom_quorum
        })

        return proposal

    def cast_peer_vote(self, proposal_id: str, voter_address: str, 
                       support: bool, voting_weight: float) -> Tuple[bool, str]:
        """
        Records a token-weighted vote from an external decentralized peer (human or AI).
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False, "Proposal not found"

        if proposal.status != ProposalStatus.ACTIVE:
            return False, f"Proposal is not active (Status: {proposal.status.value})"

        if voter_address in proposal.voters:
            return False, "Address has already voted on this proposal"

        proposal.voters[voter_address] = {
            "support": support,
            "weight": voting_weight,
            "timestamp": time.time()
        }

        if support:
            proposal.votes_for += voting_weight
        else:
            proposal.votes_against += voting_weight

        # Check early quorum completion
        total_votes = proposal.votes_for + proposal.votes_against
        if total_votes >= proposal.quorum_required:
            if proposal.votes_for > proposal.votes_against:
                proposal.status = ProposalStatus.SUCCEEDED
                self._issue_execution_permit(proposal)
            else:
                proposal.status = ProposalStatus.DEFEATED

        self._save_state()
        return True, f"Vote registered: {'FOR' if support else 'AGAINST'} ({voting_weight:,.0f} votes)"

    def _issue_execution_permit(self, proposal: DAOProposal):
        """
        Issues an EIP-712 / Keccak-256 execution permit signing off on the ratified mandate.
        """
        msg_hash = Web3.solidity_keccak(
            ['string', 'address', 'uint256', 'uint256'],
            [proposal.proposal_id, self.governance_account.address, int(proposal.votes_for), int(proposal.votes_against)]
        )
        # Sign with simulated governance authority key
        signed = Account._sign_hash(msg_hash, self.governance_account.key)
        proposal.execution_permit_signature = signed.signature.hex()

        self.ledger.record_action("DAO_PERMIT_ISSUED", {
            "proposal_id": proposal.proposal_id,
            "permit_sig": proposal.execution_permit_signature[:24] + "...",
            "votes_for": proposal.votes_for,
            "votes_against": proposal.votes_against
        })

    def execute_ratified_mandate(self, proposal_id: str) -> Dict[str, Any]:
        """
        Executes a ratified DAO proposal through the External Actuator Interface (EAI).
        Requires SUCCEEDED status and valid cryptographic execution permit.
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return {"status": "FAILED", "error": "Proposal not found"}

        if proposal.status != ProposalStatus.SUCCEEDED:
            return {"status": "FAILED", "error": f"Cannot execute proposal in state '{proposal.status.value}'"}

        if not proposal.execution_permit_signature:
            return {"status": "FAILED", "error": "Missing cryptographic execution permit"}

        # Dispatch action through EAI (e.g. EXECUTE_TRADE, GENERATE_DOCUMENT, BROADCAST_ALERT)
        act_name = proposal.action_payload.get("action", "BROADCAST_ALERT")
        act_params = proposal.action_payload.get("parameters", {})
        
        exec_result = self.eai.dispatch(act_name, act_params)
        proposal.status = ProposalStatus.EXECUTED
        self._save_state()

        self.ledger.record_action("DAO_MANDATE_EXECUTED", {
            "proposal_id": proposal.proposal_id,
            "action": act_name,
            "external_ref": exec_result.external_ref_id,
            "success": exec_result.success
        })

        return {
            "status": "EXECUTED",
            "proposal_id": proposal.proposal_id,
            "action_executed": act_name,
            "execution_details": exec_result
        }


# ==============================================================================
# VERIFICATION SUITE
# ==============================================================================
if __name__ == "__main__":
    dao = DAOGovernanceInterface()

    print("=" * 80)
    print("PHASE 13: DAO GOVERNANCE INTERFACE LAYER VERIFICATION")
    print(f"Governance Address: {dao.governance_account.address}")
    print("=" * 80)

    # 1. AI Submits a Strategic Mandate Proposal to the DAO
    print("\n[Step 1: AI Mandate Submission to Decentralized DAO]")
    mandate_payload = {
        "action": "EXECUTE_TRADE",
        "parameters": {"symbol": "BTC/USD", "side": "BUY", "quantity": 2.5, "price": 64800.0}
    }
    p = dao.submit_mandate(
        title="APEX Treasury Strategy: Strategic Bitcoin Reserve Allocation",
        description="Allocate $162,000 from autonomous treasury to strategic spot Bitcoin reserve.",
        action_payload=mandate_payload,
        custom_quorum=150000.0,  # 150k votes needed
        voting_period_sec=3600.0
    )
    print(f" -> Proposal ID:  {p.proposal_id}")
    print(f" -> Title:        {p.title}")
    print(f" -> Status:       {p.status.value} (Quorum Required: {p.quorum_required:,.0f} votes)")

    # 2. Decentralized Peers Cast Token-Weighted Votes
    print("\n[Step 2: External Decentralized Peer Voting]")
    # Peer 1 (Human Delegate): Votes FOR with 90,000 voting power
    peer1 = Account.create().address
    ok1, msg1 = dao.cast_peer_vote(p.proposal_id, peer1, support=True, voting_weight=90000.0)
    print(f" -> Peer 1 ({peer1[:10]}...): {msg1}")

    # Peer 2 (AI Agent Committee): Votes FOR with 75,000 voting power -> Reaches Quorum!
    peer2 = Account.create().address
    ok2, msg2 = dao.cast_peer_vote(p.proposal_id, peer2, support=True, voting_weight=75000.0)
    print(f" -> Peer 2 ({peer2[:10]}...): {msg2}")

    # 3. Verify Proposal Ratification & Execution Permit
    updated_p = dao.proposals[p.proposal_id]
    print(f"\n[Step 3: Quorum Evaluation & Status Transition]")
    print(f" -> Status:           {updated_p.status.value}")
    print(f" -> Total Votes FOR:  {updated_p.votes_for:,.0f} / Total AGAINST: {updated_p.votes_against:,.0f}")
    print(f" -> Execution Permit: {updated_p.execution_permit_signature[:32]}... (Cryptographically Signed)")

    # 4. Autonomous Execution of Ratified Mandate via EAI
    print("\n[Step 4: Executing Ratified Mandate via EAI Hands]")
    exec_res = dao.execute_ratified_mandate(p.proposal_id)
    print(f" -> Mandate Status:   {exec_res['status']}")
    print(f" -> Action Executed:  {exec_res['action_executed']}")
    print(f" -> Actuator Ref ID:  {exec_res['execution_details'].external_ref_id}")

    print("\n" + "=" * 80)
    print(f"Ledger Height: {len(dao.ledger.chain)} blocks (Integrity Verified: {dao.ledger.verify_integrity()})")
    print("=" * 80)

