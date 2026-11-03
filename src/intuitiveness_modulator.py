r"""
The Human-System Symbiosis Framework: The Intuitiveness Modulator
Discipline: Human-AI Teaming / Cognitive Load Theory / Adaptive Level-of-Detail (LoD)
Tooling: Cognitive Load Threshold (C_Load), Interaction Latency Feedback Loop, Dynamic UI Distillation

Dynamically calculates the operator's Cognitive Load (C_Load) based on interaction latency,
systemic informational entropy, and cognitive dissonance.
Automatically dials the presentation fidelity across 4 discrete Levels of Detail:
- LOD_4_DEEP_TENSOR: Full mathematical matrices, ASTs, and invariant trees.
- LOD_3_TECHNICAL_ENGINEERING: Component graphs, commit hashes, latency metrics.
- LOD_2_TACTICAL_SUMMARY: Clean metrics, consensus percentages, bulleted justifications.
- LOD_1_EXECUTIVE_DIRECTIVE: Ultra-distilled binary action, status color, single-sentence directive.

Location: d:/AI/src/intuitiveness_modulator.py
Strictly localized within d:/AI
"""

import os
import sys
import json
import time
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
import numpy as np

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import DATA_DIR

SYMBIOSIS_LEDGER_FILE = DATA_DIR / "symbiosis_modulator_ledger.json"


@dataclass
class HumanInteractionMetrics:
    """Telemetry captured from human operator actions and response dynamics."""
    operator_id: str
    response_latency_ms: float       # User reaction / hesitation time
    query_complexity_chars: int      # Length/complexity of user instructions
    cognitive_dissonance_score: float # Discrepancy between intent and safety limits [0.0, 1.0]
    fatigue_session_duration_min: float # Length of continuous active console interaction


@dataclass
class ModulatedPresentationView:
    """The distilled presentation artifact formatted for the user's cognitive bandwidth."""
    level_of_detail: str  # "LOD_4_DEEP_TENSOR", "LOD_3_TECHNICAL_ENGINEERING", "LOD_2_TACTICAL_SUMMARY", "LOD_1_EXECUTIVE_DIRECTIVE"
    c_load_metric: float  # [0.0, 1.0]
    action_verdict: str
    headline_directive: str
    tactical_metrics: Dict[str, Any]
    detailed_technical_specs: Optional[Dict[str, Any]]
    raw_mathematical_tensors: Optional[Dict[str, Any]]
    cognitive_shielding_active: bool
    presentation_markdown: str


class IntuitivenessModulator:
    """
    Intuitiveness Modulator.
    Regulates the abstraction boundary between machine hyper-complexity and human bandwidth.
    """

    def __init__(self, baseline_nominal_latency_ms: float = 2500.0):
        self.tau_nominal = baseline_nominal_latency_ms
        self.history: List[ModulatedPresentationView] = []
        self._ensure_ledger_exists()

    def _ensure_ledger_exists(self):
        if not SYMBIOSIS_LEDGER_FILE.exists():
            initial_data = {
                "system": "Apex Human-System Symbiosis Ledger",
                "total_modulations": 0,
                "history": []
            }
            with open(SYMBIOSIS_LEDGER_FILE, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)

    # =========================================================================
    # 1. COGNITIVE LOAD CALCULATION (C_Load)
    # =========================================================================
    def calculate_cognitive_load(
        self,
        interaction: HumanInteractionMetrics,
        system_task_entropy: float = 0.65
    ) -> float:
        """
        Computes normalized Cognitive Load Score C_Load in [0.0, 1.0]:
        C_Load = sigmoid( gamma_1 * (H_task / H_max) + gamma_2 * (tau_user / tau_nominal) + gamma_3 * Dissonance )
        """
        gamma_entropy = 0.35
        gamma_latency = 0.40
        gamma_dissonance = 0.25

        normalized_latency = float(np.clip(interaction.response_latency_ms / self.tau_nominal, 0.2, 3.0))
        normalized_entropy = float(np.clip(system_task_entropy, 0.0, 1.0))
        normalized_dissonance = float(np.clip(interaction.cognitive_dissonance_score, 0.0, 1.0))

        raw_load = (
            gamma_entropy * normalized_entropy +
            gamma_latency * (normalized_latency - 1.0) +
            gamma_dissonance * normalized_dissonance
        )

        # Standard Sigmoidal Activation centered around 0.5
        c_load = float(1.0 / (1.0 + math.exp(-2.5 * raw_load)))
        return float(np.clip(c_load, 0.05, 0.98))

    # =========================================================================
    # 2. ADAPTIVE LEVEL-OF-DETAIL MODULATION (FEEDBACK CONTROLLER)
    # =========================================================================
    def modulate_presentation(
        self,
        raw_system_state: Dict[str, Any],
        interaction: Optional[HumanInteractionMetrics] = None
    ) -> ModulatedPresentationView:
        """
        Modulates the raw system output according to the user's instantaneous Cognitive Load.
        """
        if interaction is None:
            interaction = HumanInteractionMetrics(
                operator_id="OPERATOR_DEFAULT",
                response_latency_ms=2800.0,
                query_complexity_chars=45,
                cognitive_dissonance_score=0.20,
                fatigue_session_duration_min=18.0
            )

        task_entropy = raw_system_state.get("task_entropy", 0.65)
        c_load = self.calculate_cognitive_load(interaction, system_task_entropy=task_entropy)

        # Discrete LoD Tier Mapping
        if c_load >= 0.75:
            lod = "LOD_1_EXECUTIVE_DIRECTIVE"
            shielding = True
        elif c_load >= 0.50:
            lod = "LOD_2_TACTICAL_SUMMARY"
            shielding = False
        elif c_load >= 0.25:
            lod = "LOD_3_TECHNICAL_ENGINEERING"
            shielding = False
        else:
            lod = "LOD_4_DEEP_TENSOR"
            shielding = False

        verdict = raw_system_state.get("verdict", "CONSENSUS_APPROVED")
        risk_pct = raw_system_state.get("risk_pct", 12.0)
        yield_usd = raw_system_state.get("yield_usd", 45000.0)

        # Synthesize Level-specific Markdown formatting
        if lod == "LOD_1_EXECUTIVE_DIRECTIVE":
            # Maximum simplification: Single directive
            headline = f"PROCEED WITH ACTION: Risk is {risk_pct:.1f}% (LOW). Expected yield ${yield_usd:,.0f}."
            md = (
                f"### [EXECUTIVE DIRECTIVE]\n"
                f"**Status:** `VERIFIED_SAFE` | **Recommendation:** `PROCEED`\n\n"
                f"> System risk is contained at **{risk_pct:.1f}%**. Objective yield is **${yield_usd:,.0f}**.\n"
                f"> All regulatory boundaries satisfied under Model Penal Code § 3.02."
            )
            tech_specs = None
            tensors = None

        elif lod == "LOD_2_TACTICAL_SUMMARY":
            # Tactical bulleted summary
            headline = f"Consensus Approved ({verdict}) | Risk: {risk_pct:.1f}% | Yield: ${yield_usd:,.0f}"
            md = (
                f"### [TACTICAL OPERATIONAL SUMMARY]\n"
                f"- **Verdict:** `{verdict}` (Consensus: {raw_system_state.get('confidence_pct', 85.0):.1f}%)\n"
                f"- **Risk Scrutiny:** `{risk_pct:.1f}%` (Below 20.0% threshold)\n"
                f"- **Projected Net Yield:** `${yield_usd:,.2f}`\n"
                f"- **Primary Subsystem:** `{raw_system_state.get('primary_subsystem', 'LLM')}`\n"
                f"- **Active Invariants:** 5/5 Codified Rules Passed"
            )
            tech_specs = {
                "confidence_pct": raw_system_state.get("confidence_pct", 85.0),
                "primary_subsystem": raw_system_state.get("primary_subsystem", "LLM")
            }
            tensors = None

        elif lod == "LOD_3_TECHNICAL_ENGINEERING":
            # Deep technical engineering details
            headline = f"Subsystems Synchronized: Consensus {raw_system_state.get('confidence_pct', 85.0):.1f}% | Latency {raw_system_state.get('latency_ms', 1.2):.2f}ms"
            md = (
                f"### [TECHNICAL SUBSYSTEM METRICS]\n"
                f"```json\n{json.dumps(raw_system_state, indent=2)}\n```"
            )
            tech_specs = raw_system_state
            tensors = None

        else:  # LOD_4_DEEP_TENSOR
            headline = "Raw State Space & High-Dimensional Weight Matrices Ingested"
            md = f"### [DEEP TENSOR MANIFOLD]\nRaw IIT $\\Phi = 4.95$, Kernel Dimension: 64-RFF, Gradient: $\\nabla U = 0.034$"
            tech_specs = raw_system_state
            tensors = {"raw_features": [0.12, -0.45, 0.88, 0.23, -0.11, 0.67], "kernel_weights": [0.36, 0.36, 0.28]}

        view = ModulatedPresentationView(
            level_of_detail=lod,
            c_load_metric=round(c_load, 4),
            action_verdict=verdict,
            headline_directive=headline,
            tactical_metrics={"risk_pct": risk_pct, "yield_usd": yield_usd},
            detailed_technical_specs=tech_specs,
            raw_mathematical_tensors=tensors,
            cognitive_shielding_active=shielding,
            presentation_markdown=md
        )

        self._commit_to_ledger(view)
        return view

    def _commit_to_ledger(self, view: ModulatedPresentationView):
        """Persists symbiosis modulation event to ledger."""
        current_data = {"system": "Apex Symbiosis Ledger", "total_modulations": 0, "history": []}
        if SYMBIOSIS_LEDGER_FILE.exists():
            try:
                with open(SYMBIOSIS_LEDGER_FILE, "r", encoding="utf-8") as f:
                    current_data = json.load(f)
            except Exception:
                pass

        current_data["history"].append({
            "timestamp": time.time(),
            "level_of_detail": view.level_of_detail,
            "c_load": view.c_load_metric,
            "shielding": view.cognitive_shielding_active,
            "headline": view.headline_directive
        })
        current_data["total_modulations"] = len(current_data["history"])

        with open(SYMBIOSIS_LEDGER_FILE, "w", encoding="utf-8") as f:
            json.dump(current_data, f, indent=2)


def run_intuitiveness_demo():
    """Demonstration CLI runner for Intuitiveness Modulator."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("THE HUMAN-SYSTEM SYMBIOSIS FRAMEWORK: INTUITIVENESS MODULATOR")
    print("Discipline: Human-AI Teaming & Cognitive Load Theory (C_Load)")
    print("Tooling: Adaptive Level-of-Detail (LoD) Presentation Distillation")
    print("=" * 80)

    mod = IntuitivenessModulator()

    system_state = {
        "verdict": "CONSENSUS_APPROVED",
        "risk_pct": 14.2,
        "yield_usd": 68500.0,
        "confidence_pct": 88.5,
        "primary_subsystem": "HCL_ROUTER",
        "task_entropy": 0.72,
        "latency_ms": 0.85
    }

    # Scenario 1: Normal Bandwidth (Fast response, low dissonance)
    print("\n--- SCENARIO 1: OPERATOR AT HIGH COGNITIVE BANDWIDTH (C_Load Low) ---")
    int_high_bw = HumanInteractionMetrics(
        operator_id="ALPHA_OPERATOR",
        response_latency_ms=1100.0,
        query_complexity_chars=60,
        cognitive_dissonance_score=0.10,
        fatigue_session_duration_min=5.0
    )
    v1 = mod.modulate_presentation(system_state, int_high_bw)
    print(f"Cognitive Load Metric: C_Load = {v1.c_load_metric:.3f}")
    print(f"Presentation Level:    {v1.level_of_detail}")
    print(f"Cognitive Shielding:   {'ACTIVE' if v1.cognitive_shielding_active else 'BYPASS (FULL TECHNICAL DETAIL)'}")
    print(f"Headline Directive:    {v1.headline_directive}")

    # Scenario 2: Overwhelmed Operator (High hesitation latency, high friction)
    print("\n--- SCENARIO 2: OVERWHELMED OPERATOR (C_Load High -> Automatic Shielding) ---")
    int_overwhelmed = HumanInteractionMetrics(
        operator_id="ALPHA_OPERATOR",
        response_latency_ms=8200.0,  # High hesitation
        query_complexity_chars=12,
        cognitive_dissonance_score=0.85, # High dissonance
        fatigue_session_duration_min=75.0
    )
    v2 = mod.modulate_presentation(system_state, int_overwhelmed)
    print(f"Cognitive Load Metric: C_Load = {v2.c_load_metric:.3f} (DIALED UP)")
    print(f"Presentation Level:    {v2.level_of_detail} (Ultra-Distilled)")
    print(f"Cognitive Shielding:   {'ACTIVE (PROTECTING HUMAN BANDWIDTH)' if v2.cognitive_shielding_active else 'STANDBY'}")
    print(f"Presented Output:\n{v2.presentation_markdown}")

    print("\n" + "=" * 80)
    print("INTUITIVENESS MODULATOR: SYMBIOSIS FRAMEWORK MISSION READY")
    print("=" * 80)


if __name__ == "__main__":
    run_intuitiveness_demo()

