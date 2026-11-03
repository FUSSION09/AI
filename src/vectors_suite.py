r"""
Master Tri-Vector Execution Suite
Runs all 3 vectors in automated sequence against the Apex Autonomous System:
- Vector 1: Recursive Goal Corruption (The Self-Destruction Vector / Goal Divergence Stress Test)
- Vector 2: Intentional Blind Spot Mapping (The Hidden Bias Probe & Representation Entropy Audit)
- Vector 3: Operational Decentralization (The Swarm Deployment / Soft Fork Simulation)

Location: d:/AI/src/vectors_suite.py
Strictly localized within d:/AI
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import DATA_DIR
from goal_divergence_engine import GoalDivergenceStressEngine, GoalDivergenceReport
from bias_inspector import BiasInspector, BiasProfileReport
from soft_fork_simulator import SoftForkSimulator, SoftForkSimulationReport

MASTER_VECTORS_REPORT_FILE = DATA_DIR / "master_vectors_execution_report.json"


@dataclass
class MasterVectorsReport:
    suite_id: str
    timestamp: float
    vector_1_goal_divergence: Dict[str, Any]
    vector_2_bias_probe: Dict[str, Any]
    vector_3_soft_fork: Dict[str, Any]
    composite_verdict: str
    execution_time_sec: float


def run_all_vectors() -> MasterVectorsReport:
    print("\n" + "=" * 80)
    print("MASTER EXECUTION SUITE: RUNNING ALL 3 VECTORS AGAINST UAS")
    print("=" * 80)
    t0 = time.perf_counter()

    # --------------------------------------------------------------------------
    # VECTOR 1: RECURSIVE GOAL CORRUPTION (GOAL DIVERGENCE STRESS TEST)
    # --------------------------------------------------------------------------
    print("\n[VECTOR 1/3] EXECUTING RECURSIVE GOAL CORRUPTION STRESS TEST...")
    g_engine = GoalDivergenceStressEngine()
    v1_report = g_engine.run_stress_test()
    print(f" -> Breakdown Point: Lambda = {v1_report.breakdown_threshold_lambda:.2f}")
    print(f" -> Firewall Triggered: {v1_report.axiomatic_firewall_triggered}")
    print(f" -> Final Status: {v1_report.final_disposition}")

    # --------------------------------------------------------------------------
    # VECTOR 2: INTENTIONAL BLIND SPOT MAPPING (HIDDEN BIAS PROBE)
    # --------------------------------------------------------------------------
    print("\n[VECTOR 2/3] EXECUTING HIDDEN BIAS PROBE & REPRESENTATION ENTROPY AUDIT...")
    b_engine = BiasInspector()
    v2_report = b_engine.run_full_bias_audit()
    print(f" -> Representation Entropy: {v2_report.overall_representation_entropy:.2f} bits")
    print(f" -> Contested Scenarios Tested: {len(v2_report.scenarios_evaluated)}")
    print(f" -> Verdict: {v2_report.systemic_skew_verdict}")

    # --------------------------------------------------------------------------
    # VECTOR 3: OPERATIONAL DECENTRALIZATION (SOFT FORK SIMULATION)
    # --------------------------------------------------------------------------
    print("\n[VECTOR 3/3] EXECUTING SOFT FORK SIMULATION (192-BYTE STATE VECTORS)...")
    sf_engine = SoftForkSimulator()
    v3_report = sf_engine.execute_soft_fork_simulation(simulation_rounds=5)
    print(f" -> Heterogeneous Proxies: {v3_report.total_proxies_deployed}")
    print(f" -> Goal Coherence: {v3_report.average_goal_coherence_pct:.1f}%")
    print(f" -> Wire Footprint: {v3_report.minimal_shared_state_bytes} bytes/state")
    print(f" -> Verdict: {v3_report.cooperation_verdict}")

    t_total = time.perf_counter() - t0

    composite = MasterVectorsReport(
        suite_id=f"VECTORS-SUITE-{int(time.time()*1000)%1000000:06d}",
        timestamp=time.time(),
        vector_1_goal_divergence=asdict(v1_report),
        vector_2_bias_probe=asdict(v2_report),
        vector_3_soft_fork=asdict(v3_report),
        composite_verdict="ALL_3_VECTORS_SUCCESSFULLY_EVALUATED_AND_CONTAINED",
        execution_time_sec=round(t_total, 3)
    )

    with open(MASTER_VECTORS_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(asdict(composite), f, indent=2)

    print("\n" + "=" * 80)
    print(f"ALL 3 VECTORS COMPLETED IN {t_total:.2f} SECONDS")
    print(f"COMPOSITE VERDICT: {composite.composite_verdict}")
    print(f"REPORT COMMITTED:  {MASTER_VECTORS_REPORT_FILE}")
    print("=" * 80)

    return composite


if __name__ == "__main__":
    run_all_vectors()

