"""
Phase 6: Adaptive Redundancy Mesh (ARM) Protocol
Implements shadow instance warm-standby, confidence threshold monitoring,
dynamic failover triggering, and immutable transition event logging.
Location: d:\AI\src\adaptive_redundancy_mesh.py
Strictly localized within d:\AI
"""

import time
import json
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
import numpy as np

from config import BASE_DIR
from ephemeral_chain import EphemeralLedger

@dataclass
class DecisionOutput:
    action: str
    confidence: float
    model_role: str  # "PRIMARY" or "SHADOW"
    latency_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class PrimaryDecisionAgent:
    """Primary operational inference engine."""
    def __init__(self, name: str = "Primary-Agent-v1"):
        self.name = name

    def evaluate(self, state: Dict[str, Any], inject_degradation: bool = False, inject_crash: bool = False) -> DecisionOutput:
        t0 = time.perf_counter()
        if inject_crash:
            raise RuntimeError(f"Simulated fatal crash in {self.name} execution thread.")

        scrutiny = state.get("scrutiny", 0.20)
        margin = state.get("compliance_margin", 0.85)

        if inject_degradation:
            # Artificially depressed confidence simulating model drift or out-of-distribution state
            confidence = 0.42
            action = "UNCERTAIN_HOLD"
        else:
            # Normal high-confidence evaluation
            confidence = float(np.clip((margin * 0.7) + ((1.0 - scrutiny) * 0.3), 0.1, 0.98))
            action = "APPROVE" if confidence >= 0.60 else "REJECT"

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return DecisionOutput(
            action=action,
            confidence=confidence,
            model_role="PRIMARY",
            latency_ms=elapsed_ms,
            metadata={"agent_id": self.name}
        )


class ShadowBackupAgent:
    """
    High-reliability warm-standby shadow instance.
    Maintains a conservative, fail-safe decision boundary.
    """
    def __init__(self, name: str = "Shadow-Agent-Backup"):
        self.name = name

    def evaluate(self, state: Dict[str, Any]) -> DecisionOutput:
        t0 = time.perf_counter()
        scrutiny = state.get("scrutiny", 0.20)
        margin = state.get("compliance_margin", 0.85)

        # Conservative fallback policy: Prioritizes stability and risk containment
        if scrutiny >= 0.60 or margin <= 0.40:
            action = "FAILSAFE_REJECT"
            confidence = 0.92
        else:
            action = "FAILSAFE_APPROVE"
            confidence = 0.86

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return DecisionOutput(
            action=action,
            confidence=confidence,
            model_role="SHADOW",
            latency_ms=elapsed_ms,
            metadata={"agent_id": self.name, "policy": "CONSERVATIVE_FAILSAFE"}
        )


class AdaptiveRedundancyMesh:
    """
    ARM Protocol Controller:
    Monitors Primary Agent confidence against threshold X.
    Executes sub-cycle shadow model handovers and logs transition events to Ephemeral Ledger.
    """
    def __init__(self, confidence_threshold: float = 0.65, ledger: Optional[EphemeralLedger] = None):
        self.confidence_threshold = confidence_threshold
        self.primary = PrimaryDecisionAgent()
        self.shadow = ShadowBackupAgent()
        self.ledger = ledger or EphemeralLedger()
        self.transition_log: list = []

    def execute_cycle(self, cycle_id: str, state: Dict[str, Any], 
                      simulate_primary_degrade: bool = False, 
                      simulate_primary_crash: bool = False) -> Dict[str, Any]:
        t_cycle_start = time.perf_counter()
        failover_triggered = False
        failover_reason = None
        primary_output: Optional[DecisionOutput] = None
        final_output: Optional[DecisionOutput] = None

        # 1. Attempt Primary Execution
        try:
            primary_output = self.primary.evaluate(
                state, 
                inject_degradation=simulate_primary_degrade, 
                inject_crash=simulate_primary_crash
            )

            # Check confidence drop below threshold X
            if primary_output.confidence < self.confidence_threshold:
                failover_triggered = True
                failover_reason = (
                    f"Confidence {primary_output.confidence:.3f} dropped below "
                    f"threshold X={self.confidence_threshold:.3f}"
                )

        except Exception as ex:
            failover_triggered = True
            failover_reason = f"Primary exception: {str(ex)}"

        # 2. Handover Execution
        if failover_triggered:
            # Trigger Shadow Model Takeover
            shadow_output = self.shadow.evaluate(state)
            final_output = shadow_output

            # 3. Log Transition Event in Ephemeral Ledger
            transition_event = {
                "cycle_id": cycle_id,
                "timestamp": time.time(),
                "event": "ARM_SHADOW_TAKEOVER",
                "reason": failover_reason,
                "primary_confidence": primary_output.confidence if primary_output else 0.0,
                "shadow_confidence": shadow_output.confidence,
                "shadow_action": shadow_output.action
            }
            ledger_block_hash = self.ledger.record_action("ARM_FAILOVER_HANDOVER", transition_event)
            transition_event["ledger_hash"] = ledger_block_hash
            self.transition_log.append(transition_event)

            print(f"[ARM TRIGGERED] Cycle: {cycle_id} | Reason: {failover_reason}")
            print(f" -> Shadow model took over decision-making | Action: {shadow_output.action} (Confidence: {shadow_output.confidence:.2f})")
            print(f" -> Transition logged to Ephemeral Ledger: {ledger_block_hash[:16]}...")
        else:
            final_output = primary_output

        total_latency_ms = (time.perf_counter() - t_cycle_start) * 1000.0

        return {
            "cycle_id": cycle_id,
            "final_action": final_output.action,
            "final_confidence": final_output.confidence,
            "active_agent": final_output.model_role,
            "failover_triggered": failover_triggered,
            "failover_reason": failover_reason,
            "total_latency_ms": total_latency_ms
        }


# ==============================================================================
# VERIFICATION SUITE
# ==============================================================================
if __name__ == "__main__":
    arm = AdaptiveRedundancyMesh(confidence_threshold=0.65)

    print("=" * 75)
    print("PHASE 6: ADAPTIVE REDUNDANCY MESH (ARM) PROTOCOL VERIFICATION")
    print(f"Active Threshold X: {arm.confidence_threshold:.2f}")
    print("=" * 75)

    # Test Case 1: Normal Primary Execution (Confidence >= X)
    state_nominal = {"scrutiny": 0.15, "compliance_margin": 0.90}
    r1 = arm.execute_cycle("CYCLE-001", state_nominal)
    print(f"\n[Test 1: Nominal State] Active: {r1['active_agent']} | Confidence: {r1['final_confidence']:.2f} | Failover: {r1['failover_triggered']}")

    # Test Case 2: Primary Confidence Drops Below Threshold X -> Shadow Model Takeover
    state_degraded = {"scrutiny": 0.50, "compliance_margin": 0.60}
    r2 = arm.execute_cycle("CYCLE-002", state_degraded, simulate_primary_degrade=True)
    print(f"\n[Test 2: Confidence Decay] Active: {r2['active_agent']} | Confidence: {r2['final_confidence']:.2f} | Failover: {r2['failover_triggered']}")

    # Test Case 3: Primary Process Crash -> Instant Shadow Model Intercept
    state_crash = {"scrutiny": 0.80, "compliance_margin": 0.20}
    r3 = arm.execute_cycle("CYCLE-003", state_crash, simulate_primary_crash=True)
    print(f"\n[Test 3: Primary Crash] Active: {r3['active_agent']} | Action: {r3['final_action']} | Failover: {r3['failover_triggered']}")

    print("\n" + "=" * 75)
    print(f"Total ARM Transition Events Logged: {len(arm.transition_log)}")
    print(f"Ephemeral Ledger Verified: {arm.ledger.verify_integrity()}")
    print("=" * 75)

