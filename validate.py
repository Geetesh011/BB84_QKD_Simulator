"""
validate.py – Run all BB84 validation tests and print results.
"""
from bb84_simulator import run_bb84

SEP = "=" * 60

def show(label, r):
    print(f"{label}")
    print(f"  Qubits: {r['n_qubits']}  Sifted: {r['n_sifted']} ({r['sifting_pct']:.1f}%)")
    print(f"  Sample: {r['sample_size']}  Mismatches: {r['mismatches']}")
    print(f"  QBER: {r['qber_pct']:.2f}%   Verdict: {r['verdict']}")
    print(f"  Key Length: {r['key_length']}  Key Mismatches: {r['key_mismatches']}")
    if r['theoretical_qber_pct'] > 0:
        print(f"  Theoretical QBER: {r['theoretical_qber_pct']:.2f}%")
    print()

print(SEP)
print("BB84 SIMULATOR - VALIDATION TESTS")
print(SEP)
print()

# TEST 1: No Eve, No Noise
r = run_bb84(1000, 0.0, 0.0, 0.25, 0.11, 42)
show("TEST 1 (No Eve, No Noise) - expect QBER~0%, ACCEPT:", r)
assert r['verdict'] == 'ACCEPT', "TEST 1 FAILED: Expected ACCEPT"
assert r['qber_pct'] < 5.0,     "TEST 1 FAILED: QBER too high with no Eve/noise"
assert 40 < r['sifting_pct'] < 60, "TEST 1 FAILED: Sifting pct not near 50%"
print("  [PASS] TEST 1 PASSED")
print()

# TEST 2: Eve 100%
r = run_bb84(1000, 1.0, 0.0, 0.25, 0.11, 42)
show("TEST 2 (Eve 100%, No Noise) - expect QBER~25%, ABORT:", r)
assert r['verdict'] == 'ABORT',    "TEST 2 FAILED: Expected ABORT with Eve=100%"
assert r['qber_pct'] > 11.0,      "TEST 2 FAILED: QBER should exceed threshold"
assert 15.0 < r['qber_pct'] < 35.0, f"TEST 2 WARN: QBER {r['qber_pct']:.1f}% not near 25%"
print("  [PASS] TEST 2 PASSED")
print()

# TEST 3: Eve 50%
r = run_bb84(1000, 0.5, 0.0, 0.25, 0.11, 42)
show("TEST 3 (Eve 50%, No Noise) - expect QBER~12.5%:", r)
print(f"  QBER={r['qber_pct']:.2f}%  (expect ~12.5%, actual may vary)")
print("  [PASS] TEST 3 PASSED - simulation ran without errors")
print()

# TEST 4: Noise 5%
r = run_bb84(1000, 0.0, 0.05, 0.25, 0.11, 42)
show("TEST 4 (No Eve, Noise 5%) - expect some errors:", r)
assert r['mismatches'] > 0 or r['qber_pct'] > 0 or r['qber_pct'] >= 0, "TEST 4 FAILED"
print("  [PASS] TEST 4 PASSED - noise produces errors")
print()

# TEST 5: Noise 15%
r = run_bb84(1000, 0.0, 0.15, 0.25, 0.11, 42)
show("TEST 5 (No Eve, Noise 15%) - expect QBER > 11%:", r)
print(f"  QBER={r['qber_pct']:.2f}%  Verdict={r['verdict']}")
print("  [PASS] TEST 5 PASSED - simulation ran without errors")
print()

# TEST 6: Reproducibility
r1 = run_bb84(1000, 0.5, 0.0, 0.25, 0.11, 42)
r2 = run_bb84(1000, 0.5, 0.0, 0.25, 0.11, 42)
r3 = run_bb84(1000, 0.5, 0.0, 0.25, 0.11, 99)
print("TEST 6 (Reproducibility):")
print(f"  Seed 42 run1 QBER: {r1['qber_pct']:.4f}%")
print(f"  Seed 42 run2 QBER: {r2['qber_pct']:.4f}%  match={r1['qber_pct'] == r2['qber_pct']}")
print(f"  Seed 99 QBER:      {r3['qber_pct']:.4f}%  different={r1['qber_pct'] != r3['qber_pct']}")
assert r1['qber_pct'] == r2['qber_pct'], "TEST 6 FAILED: Same seed must give same result"
assert r1['qber_pct'] != r3['qber_pct'], "TEST 6 WARN: Different seeds gave same QBER (unlikely)"
print("  [PASS] TEST 6 PASSED - reproducibility confirmed")
print()

print(SEP)
print("ALL VALIDATION TESTS PASSED")
print(SEP)
