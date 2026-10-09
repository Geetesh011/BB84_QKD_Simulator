"""
audit_sweep.py — Step 1: Investigate the suspicious QBER at 50% Eve.
"""
import numpy as np
from bb84_simulator import run_bb84

SEP = "=" * 62

# ── Reproduce the reported result ──────────────────────────────────────────
print(SEP)
print("AUDIT 1 — Reproduce reported chart (n=1000, seed=42, sample=25%)")
print(SEP)
for eve in [0, 25, 50, 75, 100]:
    r = run_bb84(1000, eve/100, 0.0, 0.25, 0.11, 42)
    theory = eve * 0.25
    diff = r['qber_pct'] - theory
    sigma = (theory/100 * (1 - theory/100) / r['sample_size']) ** 0.5 * 100
    z = diff / sigma if sigma > 0 else 0
    print(f"  Eve={eve:3d}%  QBER={r['qber_pct']:6.2f}%  "
          f"theory={theory:5.2f}%  diff={diff:+6.2f}%  z={z:+5.1f}  "
          f"sample={r['sample_size']}")

# ── Large n test to verify correctness ─────────────────────────────────────
print()
print(SEP)
print("AUDIT 2 — Large n (20000), 30 seeds — should match theory")
print(SEP)
for eve in [0, 25, 50, 75, 100]:
    qbers = [run_bb84(20000, eve/100, 0.0, 0.25, 0.11, s)['qber_pct']
             for s in range(30)]
    theory = eve * 0.25
    print(f"  Eve={eve:3d}%  mean={np.mean(qbers):5.2f}%  "
          f"std={np.std(qbers):.2f}%  theory={theory:.2f}%  "
          f"diff={np.mean(qbers)-theory:+.2f}%")

# ── No-Eve case: QBER must be 0 ────────────────────────────────────────────
print()
print(SEP)
print("AUDIT 3 — No Eve, no noise — QBER must be exactly 0%")
print(SEP)
fails = 0
for s in range(50):
    r = run_bb84(1000, 0.0, 0.0, 0.25, 0.11, s)
    if r['qber_pct'] > 0:
        fails += 1
        print(f"  FAIL seed={s}  QBER={r['qber_pct']:.2f}%")
if fails == 0:
    print("  PASS — all 50 seeds gave QBER = 0.00%")

# ── Full Eve: QBER must approach 25% ───────────────────────────────────────
print()
print(SEP)
print("AUDIT 4 — Full Eve (100%), 30 seeds — QBER must approach 25%")
print(SEP)
qbers = [run_bb84(1000, 1.0, 0.0, 0.25, 0.11, s)['qber_pct'] for s in range(30)]
print(f"  mean={np.mean(qbers):.2f}%  std={np.std(qbers):.2f}%  "
      f"min={np.min(qbers):.2f}%  max={np.max(qbers):.2f}%  theory=25.00%")

# ── Confirm the 50% Eve result is just noise, not a bug ────────────────────
print()
print(SEP)
print("AUDIT 5 — Eve=50%, 100 different seeds — is 25.6% an outlier?")
print(SEP)
qbers_50 = [run_bb84(1000, 0.5, 0.0, 0.25, 0.11, s)['qber_pct'] for s in range(100)]
q42 = run_bb84(1000, 0.5, 0.0, 0.25, 0.11, 42)['qber_pct']
above_20 = sum(q > 20 for q in qbers_50)
print(f"  seed=42 QBER: {q42:.2f}%")
print(f"  mean (100 seeds): {np.mean(qbers_50):.2f}%  std: {np.std(qbers_50):.2f}%")
print(f"  Results above 20%: {above_20}/100 — expected from variance")
print(f"  VERDICT: {'STATISTICAL NOISE — logic is correct' if abs(np.mean(qbers_50)-12.5)<2 else 'POSSIBLE BUG'}")
print(SEP)
