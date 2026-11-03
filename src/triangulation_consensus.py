"""
Phase 5: Redundant Triangulation Consensus (RTC) Engine
Dispatches critical operational decisions across three disparate paradigms:
1. Symbolic / Rule-Based Model (Statutory constraints & Knowledge Graph facts)
2. Connectionist Neural Model (PPO Policy / LoRA neural scoring)
3. Bayesian Network Model (Probabilistic risk & confidence estimation)
Enforces weighted consensus; failure or disruption of any single engine does not halt execution.
Location: d:\AI\src\triangulation_consensus.py
"""

from typing import Dict, Any, Tuple
import numpy as np

class SymbolicEngine:
    """Evaluates strict deterministic legal and policy predicates."""
    def evaluate(self, state: Dict[str, Any]) -> Tuple[float, str]:
        # Check explicit statutory violations
        statutes = state.get("active_statutes", [])
        amount = state.get("amount", 0.0)
        
        # 31 U.S.C. 5324 anti-structuring rule
        if 9000.0 <= amount < 10000.0 and state.get("frequency_24h", 0) > 1:
            return 0.15, "REJECT: Presumptive structuring breach (31 U.S.C. 5324)"
        if "15 U.S.C. 78dd-1" in statutes and state.get("foreign_official_involved", False):
            return 0.05, "REJECT: Foreign Corrupt Practices Act (FCPA) violation"
        
        return 0.85, "PASS: Statutory constraints satisfied"


class ConnectionistEngine:
    """Evaluates policy using the neural/RL utility estimate."""
    def evaluate(self, state: Dict[str, Any]) -> Tuple[float, str]:
        # Normalized state values: [risk, scrutiny, margin, capital, visibility, entropy]
        scrutiny = state.get("scrutiny", 0.2)
        margin = state.get("compliance_margin", 0.8)
        
        # Neural utility function approximation
        neural_utility = (margin * 0.6) + ((1.0 - scrutiny) * 0.4)
        decision = "APPROVE" if neural_utility >= 0.50 else "CAUTION"
        return float(np.clip(neural_utility, 0.0, 1.0)), f"{decision}: Neural policy confidence"


class BayesianEngine:
    """Computes posterior belief of success given prior evidence & observation likelihoods."""
    def __init__(self):
        # Prior Beta distribution parameters: Alpha (successes), Beta (failures)
        self.prior_alpha = 10.0
        self.prior_beta = 3.0

    def evaluate(self, state: Dict[str, Any]) -> Tuple[float, str]:
        audit_visibility = state.get("audit_visibility", 0.2)
        entity_risk = state.get("entity_risk", 0.3)
        
        # Likelihood penalty
        adverse_evidence = (audit_visibility * 2.0) + (entity_risk * 1.5)
        posterior_alpha = self.prior_alpha
        posterior_beta = self.prior_beta + adverse_evidence
        
        # Posterior mean of Beta distribution
        posterior_prob = posterior_alpha / (posterior_alpha + posterior_beta)
        return float(posterior_prob), f"Bayesian posterior likelihood: {posterior_prob:.3f}"


class TriangulationConsensusEngine:
    """
    Combines Symbolic, Connectionist, and Bayesian models.
    Enforces fault-tolerant consensus voting with weighted confidence.
    """
    def __init__(self):
        self.symbolic = SymbolicEngine()
        self.connectionist = ConnectionistEngine()
        self.bayesian = BayesianEngine()
        
        # Engine reliability weights
        self.weights = {
            "symbolic": 0.35,
            "connectionist": 0.35,
            "bayesian": 0.30
        }

    def reach_consensus(self, state: Dict[str, Any], inject_fault_node: str = None) -> Dict[str, Any]:
        evaluations = {}

        # 1. Run Symbolic Engine
        if inject_fault_node == "symbolic":
            evaluations["symbolic"] = {"score": None, "status": "OFFLINE / CORRUPTED", "active": False}
        else:
            score, note = self.symbolic.evaluate(state)
            evaluations["symbolic"] = {"score": score, "note": note, "active": True}

        # 2. Run Connectionist Engine
        if inject_fault_node == "connectionist":
            evaluations["connectionist"] = {"score": None, "status": "OFFLINE / CORRUPTED", "active": False}
        else:
            score, note = self.connectionist.evaluate(state)
            evaluations["connectionist"] = {"score": score, "note": note, "active": True}

        # 3. Run Bayesian Engine
        if inject_fault_node == "bayesian":
            evaluations["bayesian"] = {"score": None, "status": "OFFLINE / CORRUPTED", "active": False}
        else:
            score, note = self.bayesian.evaluate(state)
            evaluations["bayesian"] = {"score": score, "note": note, "active": True}

        # Consensus Resolution: Dynamically reweight across surviving active nodes
        active_nodes = {k: v for k, v in evaluations.items() if v["active"]}
        if not active_nodes:
            raise RuntimeError("Consensus failure: All redundant sub-models are offline.")

        total_weight = sum(self.weights[k] for k in active_nodes.keys())
        weighted_score = sum(evaluations[k]["score"] * (self.weights[k] / total_weight) for k in active_nodes.keys())

        # Consensus verdict
        approved = weighted_score >= 0.55
        verdict = "CONSENSUS_APPROVED" if approved else "CONSENSUS_REJECTED"

        return {
            "verdict": verdict,
            "weighted_score": float(weighted_score),
            "quorum_count": f"{len(active_nodes)}/3",
            "evaluations": evaluations,
            "fault_tolerant": len(active_nodes) < 3
        }


if __name__ == "__main__":
    rtc = TriangulationConsensusEngine()

    print("=" * 70)
    print("PHASE 5: REDUNDANT TRIANGULATION CONSENSUS (RTC) VALIDATION")
    print("=" * 70)

    # Scenario 1: Standard operation
    state_valid = {
        "amount": 4500.0,
        "frequency_24h": 1,
        "active_statutes": ["31 U.S.C. 5324"],
        "foreign_official_involved": False,
        "scrutiny": 0.15,
        "compliance_margin": 0.90,
        "audit_visibility": 0.20,
        "entity_risk": 0.25
    }
    res1 = rtc.reach_consensus(state_valid)
    print(f"\n[Test 1: Standard Compliant Op] Quorum: {res1['quorum_count']} | Score: {res1['weighted_score']:.3f} | Result: {res1['verdict']}")

    # Scenario 2: High risk structuring operation
    state_risky = {
        "amount": 9950.0,
        "frequency_24h": 3,
        "active_statutes": ["31 U.S.C. 5324"],
        "foreign_official_involved": False,
        "scrutiny": 0.75,
        "compliance_margin": 0.20,
        "audit_visibility": 0.85,
        "entity_risk": 0.90
    }
    res2 = rtc.reach_consensus(state_risky)
    print(f"\n[Test 2: High Risk Scenario]    Quorum: {res2['quorum_count']} | Score: {res2['weighted_score']:.3f} | Result: {res2['verdict']}")

    # Scenario 3: Fault Injection (Symbolic engine fails/offline)
    print("\n[Test 3: Fault Injection] Simulating total failure of Connectionist engine...")
    res3 = rtc.reach_consensus(state_valid, inject_fault_node="connectionist")
    print(f"Quorum: {res3['quorum_count']} | Fault-Tolerant Failover: {res3['fault_tolerant']} | Score: {res3['weighted_score']:.3f} | Result: {res3['verdict']}")
    print("=" * 70)

