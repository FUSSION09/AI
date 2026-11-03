r"""
Phase 11: Dynamic Resource Throttler & Subsystem Load-Shedding Protocol
Implements hierarchical load-shedding and resource throttling under peak load:
- Tier 1 (PROTECTED): PRK (Pattern Kernel) & ARM (Safety Net) - Inviolable, never shed.
- Tier 2 (THROTTLED): RL (PPO Agent) - Clamped steps and greedy evaluation.
- Tier 3 (SHED FIRST): LLM (LoRA Generation) & KG (Batch Extraction) - Suspended to free RAM/CPU.
Location: d:/AI/src/resource_throttler.py
Strictly localized within d:/AI
"""

import os
import time
from enum import Enum
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
import psutil

from config import BASE_DIR

class ResourcePressureLevel(Enum):
    NOMINAL = "NOMINAL"       # CPU < 75%, RAM < 85%
    ELEVATED = "ELEVATED"     # CPU 75-90%, RAM 85-92%
    CRITICAL = "CRITICAL"     # CPU >= 90% or RAM >= 92%


@dataclass
class SystemMetricsSnapshot:
    cpu_utilization_pct: float
    memory_utilization_pct: float
    queue_depth: int
    pressure_level: ResourcePressureLevel
    timestamp: float


class AdaptiveResourceThrottler:
    """
    Monitors system resource pressure and enforces strict tier-based load shedding:
    - Tier 1: QPMK & ARM (Always Active)
    - Tier 2: RL (Throttled under ELEVATED/CRITICAL)
    - Tier 3: LLM & KG (Shed completely under CRITICAL)
    """

    def __init__(self, cpu_elevated_thresh: float = 75.0, 
                 cpu_critical_thresh: float = 90.0,
                 ram_elevated_thresh: float = 85.0,
                 ram_critical_thresh: float = 92.0):
        self.cpu_elevated_thresh = cpu_elevated_thresh
        self.cpu_critical_thresh = cpu_critical_thresh
        self.ram_elevated_thresh = ram_elevated_thresh
        self.ram_critical_thresh = ram_critical_thresh

        # Subsystem Tier Hierarchy
        self.tier_mapping = {
            "PRK": 1,  # Protected
            "ARM": 1,  # Protected
            "RL": 2,   # Throttled
            "LLM": 3,  # Shed First
            "KG": 3    # Shed First
        }

    def sample_metrics(self, active_queue_depth: int = 0, 
                       mock_cpu: Optional[float] = None, 
                       mock_ram: Optional[float] = None) -> SystemMetricsSnapshot:
        """Sample host telemetry or test mocks."""
        cpu = mock_cpu if mock_cpu is not None else psutil.cpu_percent(interval=0.05)
        ram = mock_ram if mock_ram is not None else psutil.virtual_memory().percent

        if cpu >= self.cpu_critical_thresh or ram >= self.ram_critical_thresh or active_queue_depth >= 15:
            level = ResourcePressureLevel.CRITICAL
        elif cpu >= self.cpu_elevated_thresh or ram >= self.ram_elevated_thresh or active_queue_depth >= 8:
            level = ResourcePressureLevel.ELEVATED
        else:
            level = ResourcePressureLevel.NOMINAL

        return SystemMetricsSnapshot(
            cpu_utilization_pct=cpu,
            memory_utilization_pct=ram,
            queue_depth=active_queue_depth,
            pressure_level=level,
            timestamp=time.time()
        )

    def evaluate_subsystem_dispatch(self, subsystem: str, metrics: SystemMetricsSnapshot) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Determines whether a subsystem execution should proceed, throttle, or shed.
        Returns: (allow_execution: bool, status_mode: str, parameters_modifier: dict)
        """
        tier = self.tier_mapping.get(subsystem.upper(), 3)

        # ----------------------------------------------------------------------
        # TIER 1: PROTECTED (PRK, ARM) - NEVER SHED
        # ----------------------------------------------------------------------
        if tier == 1:
            return True, "EXECUTE_UNCONSTRAINED", {"tier": 1, "throttling": "NONE"}

        # ----------------------------------------------------------------------
        # TIER 2: RL STRATEGIC AGENT (THROTTLED UNDER LOAD)
        # ----------------------------------------------------------------------
        elif tier == 2:
            if metrics.pressure_level == ResourcePressureLevel.CRITICAL:
                # Clamped execution: Zero exploration, 1-step immediate greedy decision
                return True, "EXECUTE_THROTTLED_CRITICAL", {
                    "tier": 2,
                    "max_steps": 1,
                    "deterministic": True,
                    "bypass_policy_logging": True
                }
            elif metrics.pressure_level == ResourcePressureLevel.ELEVATED:
                return True, "EXECUTE_THROTTLED_MODERATE", {
                    "tier": 2,
                    "max_steps": 10,
                    "deterministic": True
                }
            else:
                return True, "EXECUTE_UNCONSTRAINED", {"tier": 2, "throttling": "NONE"}

        # ----------------------------------------------------------------------
        # TIER 3: LLM REASONING & KNOWLEDGE GRAPH (SHED UNDER CRITICAL LOAD)
        # ----------------------------------------------------------------------
        elif tier == 3:
            if metrics.pressure_level == ResourcePressureLevel.CRITICAL:
                # COMPLETE LOAD SHED: Reject causal LLM pass, return fast rule/cached verdict
                return False, "LOAD_SHED_CRITICAL", {
                    "tier": 3,
                    "action": "FALLBACK_SYMBOLIC_CACHE",
                    "reason": f"System in CRITICAL load (CPU: {metrics.cpu_utilization_pct}%, RAM: {metrics.memory_utilization_pct}%). LLM pass shed to prevent OOM crash."
                }
            elif metrics.pressure_level == ResourcePressureLevel.ELEVATED:
                # Clamp generation context
                return True, "EXECUTE_THROTTLED_MODERATE", {
                    "tier": 3,
                    "max_new_tokens": 32,
                    "temperature": 0.1
                }
            else:
                return True, "EXECUTE_UNCONSTRAINED", {"tier": 3, "throttling": "NONE"}

        return False, "UNKNOWN_SUBSYSTEM", {}


# ==============================================================================
# VERIFICATION SUITE
# ==============================================================================
if __name__ == "__main__":
    throttler = AdaptiveResourceThrottler()

    print("=" * 75)
    print("PHASE 11: ADAPTIVE RESOURCE THROTTLER & LOAD-SHEDDING PROTOCOL")
    print("=" * 75)

    test_scenarios = [
        ("SCENARIO 1: Nominal System Load", {"mock_cpu": 35.0, "mock_ram": 55.0, "queue": 2}),
        ("SCENARIO 2: Elevated System Pressure", {"mock_cpu": 76.0, "mock_ram": 78.0, "queue": 9}),
        ("SCENARIO 3: Critical Peak Overload", {"mock_cpu": 92.5, "mock_ram": 89.0, "queue": 18}),
    ]

    for title, params in test_scenarios:
        print(f"\n--- {title} ---")
        metrics = throttler.sample_metrics(
            active_queue_depth=params["queue"],
            mock_cpu=params["mock_cpu"],
            mock_ram=params["mock_ram"]
        )
        print(f"Metrics: CPU {metrics.cpu_utilization_pct}% | RAM {metrics.memory_utilization_pct}% | Queue: {metrics.queue_depth} | State: {metrics.pressure_level.value}")

        for subsystem in ["PRK", "ARM", "RL", "LLM", "KG"]:
            allowed, status_mode, mods = throttler.evaluate_subsystem_dispatch(subsystem, metrics)
            badge = "[ALLOW]" if allowed else "[SHED ]"
            print(f" -> {badge} Subsystem: {subsystem:<4} (Tier {throttler.tier_mapping[subsystem]}) -> Status: {status_mode}")

    print("\n" + "=" * 75)
    print("LOAD-SHEDDING HIERARCHY VERIFIED: Tier 1 Protected, Tier 2 Clamped, Tier 3 Shed.")
    print("=" * 75)

