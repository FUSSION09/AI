"""
Standalone unit test for EWMAAdaptiveThresholdGovernor.
Run from d:/AI: python src/test_ewma_unit.py
"""
import sys, math
sys.path.insert(0, "src")
from resource_throttler import EWMAAdaptiveThresholdGovernor, AdaptiveResourceThrottler

def test_ewma_governor():
    gov = EWMAAdaptiveThresholdGovernor(alpha=0.15, k=1.5, warmup_samples=10)
    throttler = AdaptiveResourceThrottler()

    # --- Cold-start (sample_count=0) ---
    snap0 = gov.current_snapshot()
    assert snap0.sample_count == 0
    assert snap0.adaptive_elevated == 75.0
    assert snap0.adaptive_critical == 90.0
    assert snap0.otv_safe is True
    print(f"[COLD]  elev={snap0.adaptive_elevated}  crit={snap0.adaptive_critical}  otv_safe={snap0.otv_safe}")

    # --- Warm-up: 15 nominal samples (20-30% CPU) ---
    nominal = [22,25,28,24,30,27,23,29,26,24,25,27,28,23,26]
    for cpu in nominal:
        snap = gov.ingest(float(cpu))
    gov.inject_into_throttler(throttler)

    assert snap.sample_count == 15
    assert snap.adaptive_elevated >= 65.0, "ELEVATED below OTV floor 65"
    assert snap.adaptive_critical <= 95.0, "CRITICAL above OTV ceiling 95"
    assert snap.adaptive_elevated <= snap.adaptive_critical, "Monotonicity violated"
    assert snap.otv_safe is True
    # Thresholds injected into throttler
    assert throttler.cpu_elevated_thresh == snap.adaptive_elevated
    assert throttler.cpu_critical_thresh == snap.adaptive_critical
    print(f"[WARM]  mu={snap.ewma_mean:.3f}  sigma={snap.ewma_sigma:.3f}  "
          f"elev={snap.adaptive_elevated}  crit={snap.adaptive_critical}  otv_safe={snap.otv_safe}")
    print(f"        throttler.elevated={throttler.cpu_elevated_thresh}  "
          f"throttler.critical={throttler.cpu_critical_thresh}")

    # --- Burst spike at 88% CPU ---
    snap_burst = gov.ingest(88.0)
    gov.inject_into_throttler(throttler)
    assert snap_burst.adaptive_critical <= 95.0, f"Burst pushed CRITICAL to {snap_burst.adaptive_critical} > 95"
    assert snap_burst.adaptive_elevated <= snap_burst.adaptive_critical, "Monotonicity violated after burst"
    assert snap_burst.otv_safe is True, "OTV safety violated after burst"
    print(f"[BURST] mu={snap_burst.ewma_mean:.3f}  sigma={snap_burst.ewma_sigma:.3f}  "
          f"crit={snap_burst.adaptive_critical}  (<=95)  otv_safe={snap_burst.otv_safe}")

    # --- Floor clamp: extreme low CPU (1%) for many iterations should not fall below 65 ---
    gov_floor = EWMAAdaptiveThresholdGovernor(alpha=0.9, k=1.5, warmup_samples=5)
    for _ in range(20):
        s = gov_floor.ingest(1.0)
    assert s.adaptive_elevated >= 65.0, f"Floor clamp failed: elevated={s.adaptive_elevated}"
    assert s.adaptive_critical >= 65.0, f"Floor clamp failed: critical={s.adaptive_critical}"
    print(f"[FLOOR] extreme-low  elev={s.adaptive_elevated}  crit={s.adaptive_critical}  (both >=65)")

    # --- Ceiling clamp: extreme high CPU (100%) should not exceed 95 ---
    gov_ceil = EWMAAdaptiveThresholdGovernor(alpha=0.9, k=1.5, warmup_samples=5)
    for _ in range(20):
        s = gov_ceil.ingest(100.0)
    assert s.adaptive_elevated <= 95.0, f"Ceiling clamp failed: elevated={s.adaptive_elevated}"
    assert s.adaptive_critical <= 95.0, f"Ceiling clamp failed: critical={s.adaptive_critical}"
    print(f"[CEIL]  extreme-high elev={s.adaptive_elevated}  crit={s.adaptive_critical}  (both <=95)")

    # --- Reset ---
    gov.reset()
    throttler.cpu_elevated_thresh = EWMAAdaptiveThresholdGovernor.STATIC_ELEVATED
    throttler.cpu_critical_thresh = EWMAAdaptiveThresholdGovernor.STATIC_CRITICAL
    snap_r = gov.current_snapshot()
    assert snap_r.sample_count == 0
    assert snap_r.adaptive_elevated == 75.0
    assert snap_r.adaptive_critical == 90.0
    assert snap_r.otv_safe is True
    print(f"[RESET] count={snap_r.sample_count}  elev={snap_r.adaptive_elevated}  "
          f"crit={snap_r.adaptive_critical}  otv_safe={snap_r.otv_safe}")

    print()
    print("ALL EWMA UNIT ASSERTIONS PASSED.")

if __name__ == "__main__":
    test_ewma_governor()

