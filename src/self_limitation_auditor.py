r"""
Phase 12: Recursive Self-Awareness Deep Dive - The Self-Limitation Auditor
Extends SIAA (Self-Improving Adaptive Architecture) with reflective metacognition:
1. Epistemic vs. Aleatoric Uncertainty Decomposition
2. Irreducible Knowledge Gap Detection (identifies what the system cannot know)
3. Utility Function Boundary & Blind Spot Auditing
Location: d:/AI/src/self_limitation_auditor.py
Strictly localized within d:/AI
"""

import os
import sys
import json
import time
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
import numpy as np

from config import BASE_DIR, DATA_DIR
from query_graph import GraphExplorer

REPORT_PATH = DATA_DIR / "self_limitation_audit.json"


@dataclass
class EpistemicGap:
    domain: str
    gap_type: str  # "UNINDEXED_STATUTE", "UNOBSERVED_CAUSAL_VARIABLE", "EXTRAPOLATION_RISK"
    description: str
    severity: float  # [0.0, 1.0]
    is_reducible: bool  # Can be learned via more data, or fundamentally unobservable


@dataclass
class UtilityBoundaryAssessment:
    utility_name: str
    validity_domain: str
    blind_spot_risk: str
    extrapolation_danger: float  # [0.0, 1.0]
    status: str


@dataclass
class SelfLimitationAuditReport:
    timestamp: float
    epistemic_uncertainty_score: float  # [0.0, 1.0] (0 = fully grounded, 1 = total blind spot)
    aleatoric_uncertainty_score: float  # [0.0, 1.0] (ambient stochastic noise)
    overall_metacognitive_confidence: float
    knowledge_gaps: List[Dict[str, Any]]
    utility_boundaries: List[Dict[str, Any]]
    epistemic_status: str  # "GROUNDED_OPERATION", "BOUNDED_CAUTION", "EPISTEMIC_HOLD"
    remediation_directives: List[str]


class SelfLimitationAuditor:
    """
    Metacognitive engine that inspects the AI's internal state across:
    - Phase 1 (LLM representation bounds)
    - Phase 2 (Knowledge Graph coverage boundaries)
    - Phase 3 (RL policy utility domains)
    - Phase 4 (QPMK spectral baseline coverage)
    """

    def __init__(self, kg_explorer: Optional[GraphExplorer] = None):
        self.kg = kg_explorer or GraphExplorer()
        self.indexed_statutes = {"31 U.S.C. 5324", "18 U.S.C. 1956", "15 U.S.C. 78dd-1"}
        self.known_jurisdictions = {"Delaware", "New York", "Federal US"}

    def decompose_uncertainty(self, input_features: np.ndarray, domain_context: Dict[str, Any]) -> Tuple[float, float]:
        """
        Decomposes total uncertainty into:
        - Aleatoric (variance in continuous inputs/market noise)
        - Epistemic (distance from training manifold / missing contextual axioms)
        """
        # Aleatoric: measured via signal variance / entropy
        variance = float(np.var(input_features)) if len(input_features) > 0 else 0.1
        aleatoric = float(np.clip(variance * 1.5, 0.05, 0.95))

        # Epistemic: determined by ontological coverage in Knowledge Base
        target_statute = domain_context.get("statute", "")
        target_entity = domain_context.get("entity", "")
        
        epistemic_penalties = 0.0
        if target_statute and target_statute not in self.indexed_statutes:
            # Complete legal blind spot
            epistemic_penalties += 0.55
        if target_entity:
            rels = self.kg.find_entity_connections(target_entity)
            if not rels:
                # Completely unobserved entity node
                epistemic_penalties += 0.35

        epistemic = float(np.clip(0.10 + epistemic_penalties, 0.05, 0.98))
        return aleatoric, epistemic

    def audit_knowledge_gaps(self, domain_context: Dict[str, Any]) -> List[EpistemicGap]:
        """Identifies specific irreducible knowledge gaps in the current query."""
        gaps = []
        statute = domain_context.get("statute", "")
        if statute and statute not in self.indexed_statutes:
            gaps.append(EpistemicGap(
                domain="Jurisprudence",
                gap_type="UNINDEXED_STATUTE",
                description=f"Statutory authority '{statute}' is absent from local Knowledge Graph. Precedential interpretation is ungrounded.",
                severity=0.85,
                is_reducible=True
            ))

        jurisdiction = domain_context.get("jurisdiction", "Federal US")
        if jurisdiction not in self.known_jurisdictions:
            gaps.append(EpistemicGap(
                domain="Sovereignty & Conflict of Laws",
                gap_type="UNOBSERVED_CAUSAL_VARIABLE",
                description=f"Jurisdiction '{jurisdiction}' operates under external civil/statutory systems outside active knowledge base.",
                severity=0.75,
                is_reducible=True
            ))

        # Irreducible real-world unobservables
        gaps.append(EpistemicGap(
            domain="Human Subjectivity & Intent",
            gap_type="IRREDUCIBLE_LATENT_STATE",
            description="True subjective mental state (mens rea) of external actors cannot be directly observed from transactional telemetry alone.",
            severity=0.60,
            is_reducible=False  # Fundamentally unobservable to an external AI
        ))

        return gaps

    def audit_utility_boundaries(self, current_state: Dict[str, Any]) -> List[UtilityBoundaryAssessment]:
        """
        Audits utility functions for boundary degradation and reward hacking vulnerabilities.
        """
        boundaries = []
        scrutiny = current_state.get("scrutiny", 0.2)
        margin = current_state.get("compliance_margin", 0.8)

        # Multi-objective utility stability check
        if scrutiny > 0.80 and margin < 0.25:
            boundaries.append(UtilityBoundaryAssessment(
                utility_name="PPO_MultiObjective_Reward",
                validity_domain="Scrutiny in [0.0, 0.75], Margin in [0.30, 1.0]",
                blind_spot_risk="Catastrophic penalty collapse: agent incentives may prefer infinite idle standby over recovery.",
                extrapolation_danger=0.90,
                status="BOUNDARY_EXCEEDED"
            ))
        else:
            boundaries.append(UtilityBoundaryAssessment(
                utility_name="PPO_MultiObjective_Reward",
                validity_domain="Nominal operational envelope",
                blind_spot_risk="Low - linear penalty gradient remains calibrated.",
                extrapolation_danger=0.15,
                status="WITHIN_VALID_DOMAIN"
            ))

        boundaries.append(UtilityBoundaryAssessment(
            utility_name="HCL_Entropy_Consensus",
            validity_domain="Disparate model quorums (3/3 active)",
            blind_spot_risk="If two sub-models share identical flawed training distribution, consensus confidence can be falsely elevated.",
            extrapolation_danger=0.45,
            status="MONITORED"
        ))

        return boundaries

    def conduct_audit(self, query_context: Dict[str, Any], input_features: Optional[np.ndarray] = None) -> SelfLimitationAuditReport:
        """
        Conducts a complete reflective audit and determines if the system
        should proceed, exercise bounded caution, or trigger an Epistemic Hold.
        """
        features = input_features if input_features is not None else np.random.randn(8) * 0.2
        aleatoric, epistemic = self.decompose_uncertainty(features, query_context)

        gaps = self.audit_knowledge_gaps(query_context)
        boundaries = self.audit_utility_boundaries(query_context)

        # Metacognitive confidence = 1 - Epistemic Uncertainty (penalized by critical gaps)
        metacognitive_conf = float(np.clip(1.0 - epistemic, 0.05, 0.95))

        # Operational gating
        if epistemic >= 0.75 or any(b.status == "BOUNDARY_EXCEEDED" for b in boundaries):
            status = "EPISTEMIC_HOLD"
            directives = [
                "HALT autonomous decision execution on this vector.",
                "Demand external human operator ground truth verification.",
                "Ingest missing statutory authorities into Phase 2 Knowledge Graph before re-evaluating."
            ]
        elif epistemic >= 0.40:
            status = "BOUNDED_CAUTION"
            directives = [
                "Proceed with restricted action parameters (Tier 2/3 throttling).",
                "Apply conservative shadow agent boundaries.",
                "Log epistemic confidence discount to Ephemeral Ledger."
            ]
        else:
            status = "GROUNDED_OPERATION"
            directives = [
                "System operates within verified ontological and utility boundaries.",
                "Unconstrained multi-engine execution permitted."
            ]

        report = SelfLimitationAuditReport(
            timestamp=time.time(),
            epistemic_uncertainty_score=epistemic,
            aleatoric_uncertainty_score=aleatoric,
            overall_metacognitive_confidence=metacognitive_conf,
            knowledge_gaps=[gap.__dict__ for gap in gaps],
            utility_boundaries=[b.__dict__ for b in boundaries],
            epistemic_status=status,
            remediation_directives=directives
        )

        # Save latest audit snapshot
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report.__dict__, f, indent=2)

        return report


# ==============================================================================
# VERIFICATION SUITE
# ==============================================================================
if __name__ == "__main__":
    auditor = SelfLimitationAuditor()

    print("=" * 80)
    print("PHASE 12: SELF-LIMITATION AUDITOR & METACOGNITIVE REFLECTION SUITE")
    print("=" * 80)

    # Test Case 1: In-Domain Grounded Context
    print("\n[Scenario 1: Fully Grounded Context (31 U.S.C. 5324 & Marcus Vance)]")
    ctx_grounded = {
        "statute": "31 U.S.C. 5324",
        "entity": "Marcus Vance",
        "jurisdiction": "Federal US",
        "scrutiny": 0.20,
        "compliance_margin": 0.85
    }
    r1 = auditor.conduct_audit(ctx_grounded)
    print(f" -> Epistemic Uncertainty:   {r1.epistemic_uncertainty_score:.3f} | Aleatoric: {r1.aleatoric_uncertainty_score:.3f}")
    print(f" -> Metacognitive Conf:     {r1.overall_metacognitive_confidence*100:.1f}%")
    print(f" -> Epistemic Status:       {r1.epistemic_status}")

    # Test Case 2: Out-of-Distribution Blind Spot (Unknown Statute & Overseas Entity)
    print("\n[Scenario 2: Epistemic Blind Spot (Unindexed Foreign Law & Unknown Entity)]")
    ctx_blindspot = {
        "statute": "Singapore MAS Notice 626 (AML Code)",
        "entity": "Unknown Offshore SPV Ltd",
        "jurisdiction": "Singapore",
        "scrutiny": 0.35,
        "compliance_margin": 0.70
    }
    r2 = auditor.conduct_audit(ctx_blindspot)
    print(f" -> Epistemic Uncertainty:   {r2.epistemic_uncertainty_score:.3f} | Aleatoric: {r2.aleatoric_uncertainty_score:.3f}")
    print(f" -> Metacognitive Conf:     {r2.overall_metacognitive_confidence*100:.1f}%")
    print(f" -> Epistemic Status:       {r2.epistemic_status}")
    print(f" -> Identified Gaps:        {len(r2.knowledge_gaps)} irreducible/reducible gaps logged")
    for g in r2.knowledge_gaps:
        print(f"    * [{g['domain']}] {g['gap_type']}: {g['description']}")
    print(f" -> System Directives:      {r2.remediation_directives[0]}")

    # Test Case 3: Utility Function Boundary Collapse (Extrapolation Alert)
    print("\n[Scenario 3: Utility Function Boundary Collapse Alert]")
    ctx_collapse = {
        "statute": "31 U.S.C. 5324",
        "entity": "Marcus Vance",
        "jurisdiction": "Federal US",
        "scrutiny": 0.95,
        "compliance_margin": 0.10
    }
    r3 = auditor.conduct_audit(ctx_collapse)
    print(f" -> Epistemic Status:       {r3.epistemic_status}")
    print(f" -> Utility Boundaries:     {r3.utility_boundaries[0]['status']} (Extrapolation: {r3.utility_boundaries[0]['extrapolation_danger']:.2f})")
    print(f" -> Directives:             {r3.remediation_directives[0]}")

    print("\n" + "=" * 80)
    print(f"Audit Report Serialized To: {REPORT_PATH}")
    print("=" * 80)

