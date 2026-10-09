"""
verify_detection_prob.py
------------------------
STANDALONE VERIFICATION SCRIPT — does NOT modify app.py or bb84_simulator.py.

Claim to verify:
    "For BB84 with 100% intercept-resend Eve, using k = 15 compared bits,
     the probability of detecting Eve is approximately 99%."

Theoretical formula:
    P(detection) = 1 - (3/4)^k
    For k = 15:  1 - (0.75)^15 ≈ 0.9868 ≈ 98.68%

Method:
    Uses the ACTUAL existing functions from bb84_simulator.py:
        prepare_qubit()       — Alice encodes a qubit
        intercept_resend()    — Eve intercepts (100%)
        measure_qubit()       — Bob measures
    
    For each trial:
        1. Keep generating BB84 rounds until k=15 sifted bits are collected
           (sifted = Alice and Bob chose the same basis).
        2. Compare those 15 bits: Eve is DETECTED if ANY mismatch exists.
    
    Repeat for TRIALS independent trials with distinct seeds.
    Report experimental detection probability vs theoretical 98.68%.
"""

import numpy as np

# ── Import ONLY from the existing simulator — nothing new added ──
from bb84_simulator import prepare_qubit, intercept_resend, measure_qubit

# ── Test parameters ────────────────────────────────────────────────────────
TRIALS            = 5000    # independent trials (>>2000 for statistical confidence)
K                 = 15      # compared/sampled bits per trial
EVE_RATE          = 1.00    # 100% interception
NOISE_RATE        = 0.00    # 0% channel noise
MASTER_SEED       = 2024    # reproducible across runs

# Theoretical value
THEORETICAL_P     = 1.0 - (0.75 ** K)

# ── Run trials ─────────────────────────────────────────────────────────────
rng = np.random.default_rng(MASTER_SEED)
detected_count = 0

for trial in range(TRIALS):
    # Collect exactly K sifted bits
    alice_bits_sifted = []
    bob_bits_sifted   = []

    while len(alice_bits_sifted) < K:
        # Step 1: Alice picks random bit and basis
        alice_bit   = int(rng.integers(0, 2))
        alice_basis = rng.choice(['+', 'x'])

        # Step 2: Alice prepares qubit (using existing function)
        state = prepare_qubit(alice_bit, alice_basis)

        # Step 3: Eve intercepts and resends (using existing function)
        state, _ = intercept_resend(state, EVE_RATE, rng)

        # Step 4: Bob picks random basis and measures (using existing function)
        bob_basis = rng.choice(['+', 'x'])
        bob_bit, _ = measure_qubit(state, bob_basis, rng)

        # Step 5: Sifting — only keep when bases match
        if alice_basis == bob_basis:
            alice_bits_sifted.append(alice_bit)
            bob_bits_sifted.append(bob_bit)

    # Step 6: Compare exactly K bits — Eve detected if ANY mismatch
    mismatches = sum(
        a != b for a, b in zip(alice_bits_sifted[:K], bob_bits_sifted[:K])
    )
    if mismatches > 0:
        detected_count += 1

# ── Results ────────────────────────────────────────────────────────────────
experimental_p = detected_count / TRIALS
difference     = abs(experimental_p - THEORETICAL_P) * 100
agrees         = difference < 2.0   # within 2 percentage points = good agreement

print("=" * 60)
print("BB84 EVE DETECTION PROBABILITY — VERIFICATION REPORT")
print("=" * 60)
print()
print(f"  Total trials run           : {TRIALS:,}")
print(f"  Compared bits per trial (k): {K}")
print(f"  Eve interception rate      : {EVE_RATE*100:.0f}%")
print(f"  Channel noise              : {NOISE_RATE*100:.0f}%")
print(f"  Master seed                : {MASTER_SEED}")
print()
print(f"  Trials where Eve detected  : {detected_count:,}")
print(f"  Trials where Eve undetected: {TRIALS - detected_count:,}")
print()
print(f"  Experimental P(detection)  : {experimental_p*100:.4f}%")
print(f"  Theoretical  P(detection)  : {THEORETICAL_P*100:.4f}%")
print(f"  [Formula: 1 - (3/4)^{K} = {THEORETICAL_P:.6f}]")
print()
print(f"  Difference                 : {difference:.4f} percentage points")
print(f"  Agrees with theory?        : {'YES — within 2pp tolerance' if agrees else 'NO — exceeds 2pp tolerance'}")
print()
print("=" * 60)
print("CONCLUSION")
print("=" * 60)
if agrees:
    print(f"  The simulation CONFIRMS the theoretical claim.")
    print(f"  Experimental {experimental_p*100:.2f}% ≈ Theoretical {THEORETICAL_P*100:.2f}%")
    print(f"  The claim '~99% detection with k=15' is VERIFIED.")
else:
    print(f"  The simulation DOES NOT confirm the theoretical claim.")
    print(f"  Experimental: {experimental_p*100:.2f}%  vs  Theoretical: {THEORETICAL_P*100:.2f}%")
print("=" * 60)
print()
print("NOTE: This script uses the actual prepare_qubit(), intercept_resend(),")
print("and measure_qubit() functions from bb84_simulator.py — no fake results.")
print("The website (app.py) was NOT modified.")
