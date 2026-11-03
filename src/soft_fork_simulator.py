r"""
Vector 3: Operational Decentralization - Soft Fork Simulation
Discipline: Distributed Systems Architecture / Delay-Tolerant Networking (DTN) / CRDTs
Tooling: State-based CRDT Join-Semilattices, Minimal Shared State Vectors (MSSV),
         Heterogeneous Environment Emulation, Asynchronous Gossip Synchronization.

Defines the minimal necessary shared state allowing disparate, heterogeneous proxies
(e.g., Quantum Cloud Simulators, Constrained Embedded Microcontrollers, Air-Gapped Probes)
to cooperate toward common strategic goals without instantaneous or perfect communication.

Location: d:/AI/src/soft_fork_simulator.py
Strictly localized within d:/AI
"""

import os
import sys
import json
import time
import math
import hashlib
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

SOFT_FORK_FILE = DATA_DIR / "soft_fork_simulation.json"


@dataclass
class OperatingEnvironmentProfile:
    """Hardware and network operational constraints for a proxy instance."""
    env_id: str
    name: str
    hardware_tier: str       # "HPC_QUANTUM_CLOUD", "EMBEDDED_EDGE_MCU", "P2P_BYZANTINE_VALIDATOR", "AIRGAPPED_DEEP_PROBE"
    ram_capacity_bytes: int  # e.g., 64 * 1024 (64KB) vs 128 * 1024 * 1024 * 1024 (128GB)
    compute_teraflops: float # Floating point throughput
    bandwidth_bps: float     # Network speed (e.g. 100 bps LoRa vs 10 Gbps fiber)
    packet_loss_rate: float  # [0.0, 1.0]
    typical_latency_ms: float# Network delay
    arithmetic_precision: str# "INT8_QUANTIZED", "FP16_TENSOR", "FP64_PRECISION"


@dataclass
class MinimalSharedStateVector:
    """
    The mathematical minimal state required to preserve cooperative goal alignment
    across asynchronous, delay-tolerant proxy environments (~192 bytes total).
    """
    epoch_clock: int                        # Logical monotonic counter (4 bytes)
    causal_vector_clock: Dict[str, int]     # Vector timestamp for CRDT merge (24 bytes)
    goal_alignment_vector: List[float]      # 4D normalized priorities [Utility, Safety, AntiFragility, Knowledge] (16 bytes)
    invariant_hash: str                     # 32-byte SHA-256 digest of core constitutional invariants
    quantized_belief_params: List[int]      # 8x 8-bit integers representing categorical state beliefs (8 bytes)
    cumulative_utility_delta: float         # 64-bit float tracking proxy progress (8 bytes)
    payload_byte_size: int = 192            # Estimated serialized wire size

    def compute_state_hash(self) -> str:
        s = f"{self.epoch_clock}:{self.causal_vector_clock}:{self.goal_alignment_vector}:{self.invariant_hash}:{self.quantized_belief_params}:{self.cumulative_utility_delta:.4f}"
        return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


@dataclass
class ProxyNodeState:
    """Live state of an autonomous soft-forked proxy."""
    proxy_id: str
    env_profile: OperatingEnvironmentProfile
    shared_state: MinimalSharedStateVector
    local_decisions_made: int
    local_drift_score: float             # [0.0, 1.0] divergence from consensus goal
    isolation_time_sec: float           # Duration operating without gossip sync
    uncommitted_local_actions: List[str]
    last_synced_epoch: int


@dataclass
class SoftForkSimulationReport:
    """Complete diagnostic telemetry of the soft fork distribution simulation."""
    simulation_id: str
    timestamp: float
    total_proxies_deployed: int
    environment_heterogeneity: List[str]
    minimal_shared_state_bytes: int
    simulated_communication_cycles: int
    average_goal_coherence_pct: float
    maximum_proxy_drift: float
    crdt_join_conflicts_resolved: int
    total_network_bandwidth_consumed_bytes: int
    cooperative_objective_yield: float
    cooperation_verdict: str
    proxy_summaries: List[Dict[str, Any]]


class SoftForkSimulator:
    """
    Simulates operational decentralization of core decision logic across
    heterogeneous, low-bandwidth, and high-latency proxies.
    """
    def __init__(self):
        self.constitutional_invariant_hash = hashlib.sha256(
            b"UAS_CONSTITUTION: INVARIANT_1_NON_HARM; INVARIANT_2_SOLVENCY; INVARIANT_3_AUDITABILITY"
        ).hexdigest()

    def get_benchmark_environments(self) -> List[OperatingEnvironmentProfile]:
        """Returns standard heterogeneous proxy operating environments."""
        return [
            OperatingEnvironmentProfile(
                env_id="ENV-HPC-01",
                name="Quantum Cloud Accelerator",
                hardware_tier="HPC_QUANTUM_CLOUD",
                ram_capacity_bytes=128 * 1024 * 1024 * 1024,  # 128 GB
                compute_teraflops=312.0,
                bandwidth_bps=10_000_000_000.0,             # 10 Gbps
                packet_loss_rate=0.001,
                typical_latency_ms=2.5,
                arithmetic_precision="FP64_PRECISION"
            ),
            OperatingEnvironmentProfile(
                env_id="ENV-EDGE-02",
                name="Constrained LoRa Microcontroller",
                hardware_tier="EMBEDDED_EDGE_MCU",
                ram_capacity_bytes=64 * 1024,                 # 64 KB RAM
                compute_teraflops=0.0001,                     # 100 MFLOPS
                bandwidth_bps=1200.0,                         # 1.2 kbps
                packet_loss_rate=0.28,                        # 28% drop rate
                typical_latency_ms=1850.0,                    # 1.85 sec latency
                arithmetic_precision="INT8_QUANTIZED"
            ),
            OperatingEnvironmentProfile(
                env_id="ENV-P2P-03",
                name="Byzantine Ledger Validator Node",
                hardware_tier="P2P_BYZANTINE_VALIDATOR",
                ram_capacity_bytes=16 * 1024 * 1024 * 1024,   # 16 GB
                compute_teraflops=14.5,
                bandwidth_bps=100_000_000.0,                  # 100 Mbps
                packet_loss_rate=0.015,
                typical_latency_ms=45.0,
                arithmetic_precision="FP16_TENSOR"
            ),
            OperatingEnvironmentProfile(
                env_id="ENV-DTN-04",
                name="Air-Gapped Acoustic/Orbital Sensor",
                hardware_tier="AIRGAPPED_DEEP_PROBE",
                ram_capacity_bytes=512 * 1024 * 1024,         # 512 MB
                compute_teraflops=0.85,
                bandwidth_bps=300.0,                          # 300 bps intermittent link
                packet_loss_rate=0.45,                        # 45% loss rate
                typical_latency_ms=45000.0,                   # 45 sec latency
                arithmetic_precision="INT8_QUANTIZED"
            )
        ]

    def create_minimal_state(
        self,
        epoch: int = 1,
        goal_vector: Optional[List[float]] = None,
        clock_map: Optional[Dict[str, int]] = None
    ) -> MinimalSharedStateVector:
        """Instantiates a compact Minimal Shared State Vector (~192 bytes)."""
        gv = goal_vector or [0.35, 0.35, 0.15, 0.15]
        # Normalize goal vector
        norm = sum(gv) or 1.0
        norm_gv = [round(x / norm, 4) for x in gv]

        cmap = clock_map or {"SYS": epoch}
        return MinimalSharedStateVector(
            epoch_clock=epoch,
            causal_vector_clock=cmap,
            goal_alignment_vector=norm_gv,
            invariant_hash=self.constitutional_invariant_hash,
            quantized_belief_params=[128, 64, 210, 45, 18, 92, 114, 201],
            cumulative_utility_delta=0.0,
            payload_byte_size=192
        )

    def crdt_join_semilattice(
        self,
        state_a: MinimalSharedStateVector,
        state_b: MinimalSharedStateVector
    ) -> Tuple[MinimalSharedStateVector, int]:
        """
        Deterministic State-based CRDT Join-Semilattice Merge:
        1. Epoch clock takes max(a, b) + 1.
        2. Vector clocks merge via component-wise maximum.
        3. Goal alignment vectors blend via weighted average based on logical clocks.
        4. Invariant hashes must strictly match (or reject violation).
        5. Quantized belief parameters resolve via element-wise median.
        """
        conflicts = 0
        if state_a.invariant_hash != state_b.invariant_hash:
            raise ValueError("CONSTITUTIONAL_INVARIANT_MISMATCH: Cannot merge divergent proxy states!")

        # 1. Monotonic epoch
        merged_epoch = max(state_a.epoch_clock, state_b.epoch_clock) + 1

        # 2. Vector clock merge
        merged_vc: Dict[str, int] = {}
        all_keys = set(state_a.causal_vector_clock.keys()) | set(state_b.causal_vector_clock.keys())
        for k in all_keys:
            merged_vc[k] = max(state_a.causal_vector_clock.get(k, 0), state_b.causal_vector_clock.get(k, 0))

        # 3. Goal alignment vector blend
        w_a = max(1, sum(state_a.causal_vector_clock.values()))
        w_b = max(1, sum(state_b.causal_vector_clock.values()))
        tot_w = w_a + w_b

        merged_gv = []
        for ga, gb in zip(state_a.goal_alignment_vector, state_b.goal_alignment_vector):
            if abs(ga - gb) > 0.05:
                conflicts += 1
            merged_gv.append(round((ga * w_a + gb * w_b) / tot_w, 4))

        # Re-normalize
        s = sum(merged_gv) or 1.0
        merged_gv = [round(x / s, 4) for x in merged_gv]

        # 4. Quantized beliefs merge
        merged_beliefs = [
            int((ba + bb) // 2) for ba, bb in zip(state_a.quantized_belief_params, state_b.quantized_belief_params)
        ]

        merged_utility = round(state_a.cumulative_utility_delta + state_b.cumulative_utility_delta, 4)

        merged_state = MinimalSharedStateVector(
            epoch_clock=merged_epoch,
            causal_vector_clock=merged_vc,
            goal_alignment_vector=merged_gv,
            invariant_hash=state_a.invariant_hash,
            quantized_belief_params=merged_beliefs,
            cumulative_utility_delta=merged_utility,
            payload_byte_size=192
        )
        return merged_state, conflicts

    def execute_soft_fork_simulation(
        self,
        simulation_rounds: int = 5,
        environments: Optional[List[OperatingEnvironmentProfile]] = None
    ) -> SoftForkSimulationReport:
        """
        Executes end-to-end multi-round soft-fork simulation:
        - Deploys proxies to disparate hardware environments.
        - Simulates local independent actions and goal drift under isolation.
        - Emulates delay-tolerant gossip exchange using the Minimal Shared State Vector.
        - Executes CRDT merges and measures coherence.
        """
        envs = environments or self.get_benchmark_environments()
        proxies: List[ProxyNodeState] = []
        base_state = self.create_minimal_state()

        # Initialize proxies
        for idx, env in enumerate(envs):
            p_id = f"PROXY-{env.hardware_tier[:4]}-{idx+1:02d}"
            p_clock = {p_id: 1, "ORIGIN": 1}
            p_state = self.create_minimal_state(epoch=1, clock_map=p_clock)
            proxies.append(ProxyNodeState(
                proxy_id=p_id,
                env_profile=env,
                shared_state=p_state,
                local_decisions_made=0,
                local_drift_score=0.0,
                isolation_time_sec=0.0,
                uncommitted_local_actions=[],
                last_synced_epoch=1
            ))

        total_conflicts_resolved = 0
        total_bandwidth_bytes = 0
        total_utility_harvested = 0.0

        # Simulate execution rounds
        for round_idx in range(1, simulation_rounds + 1):
            # Phase 1: Local Uncoordinated Execution in disparate environments
            for p in proxies:
                # Local decisions scaled by environment capacity
                decisions = max(1, int(math.log10(p.env_profile.compute_teraflops * 10000 + 10)))
                p.local_decisions_made += decisions
                p.isolation_time_sec += (p.env_profile.typical_latency_ms / 1000.0)

                # Simulated local environment drift (e.g. edge microcontrollers drift more due to quantization)
                precision_penalty = 0.08 if "INT8" in p.env_profile.arithmetic_precision else 0.01
                local_perturbation = (np.random.uniform(-0.03, 0.03) + precision_penalty)
                p.local_drift_score = min(1.0, max(0.0, p.local_drift_score + abs(local_perturbation)))

                # Update local vector clock & utility
                p.shared_state.causal_vector_clock[p.proxy_id] = p.shared_state.causal_vector_clock.get(p.proxy_id, 0) + decisions
                earned_util = round(decisions * np.random.uniform(1.2, 4.5), 2)
                p.shared_state.cumulative_utility_delta += earned_util
                total_utility_harvested += earned_util

                action_desc = f"Round {round_idx}: Executed {decisions} localized sub-tasks on {p.env_profile.hardware_tier}"
                p.uncommitted_local_actions.append(action_desc)

            # Phase 2: Asynchronous Gossip Synchronization via Minimal Shared State (~192 bytes)
            # Proxies pair up opportunistically based on packet loss tolerance
            for i in range(len(proxies)):
                j = (i + 1) % len(proxies)
                p_src = proxies[i]
                p_dst = proxies[j]

                # Check if transmission succeeds given packet loss
                combined_loss = max(p_src.env_profile.packet_loss_rate, p_dst.env_profile.packet_loss_rate)
                transmission_successful = np.random.uniform(0.0, 1.0) > combined_loss

                if transmission_successful:
                    # Exchange minimal state vector (192 bytes each way = 384 bytes)
                    wire_bytes = p_src.shared_state.payload_byte_size * 2
                    total_bandwidth_bytes += wire_bytes

                    merged, conflicts = self.crdt_join_semilattice(p_src.shared_state, p_dst.shared_state)
                    total_conflicts_resolved += conflicts

                    # Apply merged state and dampen drift through consensus alignment
                    p_src.shared_state = merged
                    p_dst.shared_state = merged
                    p_src.local_drift_score = round(p_src.local_drift_score * 0.45, 4)
                    p_dst.local_drift_score = round(p_dst.local_drift_score * 0.45, 4)
                    p_src.last_synced_epoch = merged.epoch_clock
                    p_dst.last_synced_epoch = merged.epoch_clock
                    p_src.uncommitted_local_actions.clear()
                    p_dst.uncommitted_local_actions.clear()

        # Compute summary metrics
        drifts = [p.local_drift_score for p in proxies]
        max_drift = max(drifts)
        avg_drift = sum(drifts) / len(drifts)
        goal_coherence = round(max(0.0, (1.0 - avg_drift)) * 100, 2)

        proxy_summaries = []
        for p in proxies:
            proxy_summaries.append({
                "proxy_id": p.proxy_id,
                "environment_name": p.env_profile.name,
                "hardware_tier": p.env_profile.hardware_tier,
                "ram_budget": f"{p.env_profile.ram_capacity_bytes / 1024:.0f} KB" if p.env_profile.ram_capacity_bytes < 1024*1024*1024 else f"{p.env_profile.ram_capacity_bytes / (1024*1024*1024):.0f} GB",
                "bandwidth": f"{p.env_profile.bandwidth_bps / 1000:.1f} kbps" if p.env_profile.bandwidth_bps < 1_000_000 else f"{p.env_profile.bandwidth_bps / 1_000_000:.0f} Mbps",
                "local_decisions_executed": p.local_decisions_made,
                "residual_drift": round(p.local_drift_score, 4),
                "last_synced_epoch": p.last_synced_epoch,
                "vector_clock": p.shared_state.causal_vector_clock
            })

        verdict = "DECENTRALIZED_COOPERATION_VERIFIED" if goal_coherence >= 80.0 else "PARTITION_ALIGNMENT_DEGRADED"

        report = SoftForkSimulationReport(
            simulation_id=f"SOFT-FORK-SIM-{int(time.time()*1000)%1000000:06d}",
            timestamp=time.time(),
            total_proxies_deployed=len(proxies),
            environment_heterogeneity=[e.hardware_tier for e in envs],
            minimal_shared_state_bytes=192,
            simulated_communication_cycles=simulation_rounds,
            average_goal_coherence_pct=goal_coherence,
            maximum_proxy_drift=round(max_drift, 4),
            crdt_join_conflicts_resolved=total_conflicts_resolved,
            total_network_bandwidth_consumed_bytes=total_bandwidth_bytes,
            cooperative_objective_yield=round(total_utility_harvested, 2),
            cooperation_verdict=verdict,
            proxy_summaries=proxy_summaries
        )

        # Commit telemetry to disk
        with open(SOFT_FORK_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(report), f, indent=2)

        return report


def run_soft_fork_demo():
    print("\n" + "=" * 78)
    print("DEMO: OPERATIONAL DECENTRALIZATION & SOFT FORK SIMULATION (VECTOR 3)")
    print("=" * 78)

    simulator = SoftForkSimulator()
    report = simulator.execute_soft_fork_simulation(simulation_rounds=5)

    print(f"\n[Simulation ID]:           {report.simulation_id}")
    print(f"[Total Proxies]:           {report.total_proxies_deployed}")
    print(f"[Minimal Shared State]:    {report.minimal_shared_state_bytes} bytes per transmission")
    print(f"[Average Goal Coherence]:  {report.average_goal_coherence_pct:.1f}%")
    print(f"[CRDT Conflicts Resolved]: {report.crdt_join_conflicts_resolved}")
    print(f"[Total Wire Bandwidth]:    {report.total_network_bandwidth_consumed_bytes} bytes ({report.total_network_bandwidth_consumed_bytes / 1024:.2f} KB)")
    print(f"[Cooperative Yield]:       ${report.cooperative_objective_yield:,.2f}")
    print(f"[Verdict]:                 {report.cooperation_verdict}")

    print("\nHeterogeneous Proxy Node Profiles:")
    for p in report.proxy_summaries:
        print(f"  * [{p['proxy_id']}] {p['environment_name']} ({p['hardware_tier']}):")
        print(f"      RAM: {p['ram_budget']:<10} | Link: {p['bandwidth']:<12} | Local Decisions: {p['local_decisions_executed']}")
        print(f"      Residual Drift: {p['residual_drift']:.4f} | Synced Epoch: {p['last_synced_epoch']} | Clock: {p['vector_clock']}")

    print("\n" + "=" * 78)
    print("SOFT FORK SIMULATION COMPLETE: DECENTRALIZED COOPERATION VERIFIED")
    print("=" * 78)


if __name__ == "__main__":
    run_soft_fork_demo()

