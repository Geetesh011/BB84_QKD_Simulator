"""
bb84_core.py
------------
Extended BB84 core: wraps bb84_simulator.py and adds full-trace runs,
multi-trial sweeps, and detection-probability sweeps.

All core protocol logic lives in bb84_simulator.py — unchanged.
"""

import numpy as np
import pandas as pd

from bb84_simulator import (
    prepare_qubit, measure_qubit, intercept_resend,
    apply_noise, sift_key, calculate_qber,
    extract_candidate_key, run_bb84,
    X_GATE,
)

# ── Wilson 95% confidence interval ────────────────────────────────────────

def wilson_ci(p_hat: float, n: int, z: float = 1.96):
    """Return (lo, hi) Wilson CI for a proportion."""
    if n == 0:
        return 0.0, 1.0
    denom = 1 + z**2 / n
    centre = (p_hat + z**2 / (2 * n)) / denom
    half = z * ((p_hat * (1 - p_hat) / n) + z**2 / (4 * n**2)) ** 0.5 / denom
    return max(0.0, centre - half), min(1.0, centre + half)


# ── Full-trace run ─────────────────────────────────────────────────────────

def run_full_trace(
    n_qubits: int,
    eve_interception_rate: float,
    noise_rate: float,
    sample_fraction: float,
    qber_threshold: float,
    seed: int,
) -> dict:
    """
    Run BB84 end-to-end and return a rich result dict that includes:
      - All summary metrics (same as run_bb84)
      - Per-qubit trace as a Pandas DataFrame
      - Ground-truth fields invisible to a real Alice/Bob
      - Wilson 95% CI for the QBER estimate
    """
    rng = np.random.default_rng(seed)

    # ── Step 1: Alice encodes ──────────────────────────────────────────────
    alice_bits  = rng.integers(0, 2, size=n_qubits).tolist()
    alice_bases = rng.choice(["+", "x"], size=n_qubits).tolist()
    qubit_states = [prepare_qubit(b, basis)
                    for b, basis in zip(alice_bits, alice_bases)]

    # ── Step 2: Eve ────────────────────────────────────────────────────────
    post_eve_states  = []
    intercepted_flags = []
    for state in qubit_states:
        new_state, flag = intercept_resend(state, eve_interception_rate, rng)
        post_eve_states.append(new_state)
        intercepted_flags.append(flag)

    # ── Step 3: Channel noise (track which qubits were actually flipped) ───
    post_noise_states = []
    noise_flipped     = []
    for state in post_eve_states:
        if rng.random() < noise_rate:
            post_noise_states.append(X_GATE @ state)
            noise_flipped.append(True)
        else:
            post_noise_states.append(state)
            noise_flipped.append(False)

    # ── Step 4: Bob measures ───────────────────────────────────────────────
    bob_bases = rng.choice(["+", "x"], size=n_qubits).tolist()
    bob_bits  = []
    for state, basis in zip(post_noise_states, bob_bases):
        bit, _ = measure_qubit(state, basis, rng)
        bob_bits.append(bit)

    # ── Step 5: Sifting ────────────────────────────────────────────────────
    alice_sifted, bob_sifted, sifted_orig_indices = sift_key(
        alice_bits, alice_bases, bob_bits, bob_bases
    )
    n_sifted = len(alice_sifted)

    # ── Step 6: QBER estimate ──────────────────────────────────────────────
    qber_result = calculate_qber(alice_sifted, bob_sifted, sample_fraction, rng)
    qber        = qber_result["qber"]
    accepted    = qber <= qber_threshold
    verdict     = "ACCEPT" if accepted else "ABORT"

    # ── Step 7: Candidate key ──────────────────────────────────────────────
    alice_key, bob_key = [], []
    key_mismatches = 0
    if accepted and n_sifted > 0:
        alice_key, bob_key = extract_candidate_key(
            alice_sifted, bob_sifted, qber_result["sample_indices"]
        )
        key_mismatches = sum(a != b for a, b in zip(alice_key, bob_key))

    # ── Ground truth (invisible to real Alice/Bob) ─────────────────────────
    n_intercepted   = sum(intercepted_flags)
    n_noise_flipped = sum(noise_flipped)

    # Actual error rate in the full sifted key (before removing sample bits)
    actual_errors   = sum(a != b for a, b in zip(alice_sifted, bob_sifted))
    actual_err_rate = actual_errors / n_sifted if n_sifted > 0 else 0.0

    # Wilson 95% CI for the QBER sample estimate
    k      = qber_result["sample_size"]
    lo, hi = wilson_ci(qber, k)

    # ── Per-qubit trace DataFrame ──────────────────────────────────────────
    # Map sifted-array index → original qubit index
    orig_to_sifted = {orig: si for si, orig in enumerate(sifted_orig_indices)}
    # Which original indices were in the QBER sample
    sample_orig = set(sifted_orig_indices[si] for si in qber_result["sample_indices"])

    rows = []
    for i in range(n_qubits):
        in_sift  = alice_bases[i] == bob_bases[i]
        in_sample = i in sample_orig if in_sift else False
        is_error  = (alice_bits[i] != bob_bits[i]) if in_sift else False

        rows.append({
            "Qubit #":         i + 1,
            "Alice bit":       alice_bits[i],
            "Alice basis":     alice_bases[i],
            "Eve intercepted": "Yes" if intercepted_flags[i] else "No",
            "Noise flipped":   "Yes" if noise_flipped[i] else "No",
            "Bob basis":       bob_bases[i],
            "Bob bit":         bob_bits[i],
            "Bases match":     "Yes" if in_sift else "No",
            "In sifted key":   "Yes" if in_sift else "No",
            "In QBER sample":  "Yes" if in_sample else ("No" if in_sift else "—"),
            "Error":           "Yes" if (in_sample and is_error) else
                               ("No"  if in_sample else "—"),
        })

    trace_df = pd.DataFrame(rows)

    return {
        # Core summary
        "n_qubits":              n_qubits,
        "eve_interception_rate": eve_interception_rate,
        "noise_rate":            noise_rate,
        "sample_fraction":       sample_fraction,
        "qber_threshold":        qber_threshold,
        "seed":                  seed,
        "n_sifted":              n_sifted,
        "sifting_pct":           n_sifted / n_qubits * 100,
        "sample_size":           k,
        "mismatches":            qber_result["mismatches"],
        "qber":                  qber,
        "qber_pct":              qber * 100,
        "verdict":               verdict,
        "accepted":              accepted,
        "alice_key":             alice_key,
        "bob_key":               bob_key,
        "key_length":            len(alice_key),
        "key_mismatches":        key_mismatches,
        "theoretical_qber_pct":  eve_interception_rate * 25.0,
        # Ground truth
        "n_intercepted":         n_intercepted,
        "n_noise_flipped":       n_noise_flipped,
        "actual_errors_sifted":  actual_errors,
        "actual_err_rate_pct":   actual_err_rate * 100,
        "wilson_lo_pct":         lo * 100,
        "wilson_hi_pct":         hi * 100,
        # Trace
        "trace_df":              trace_df,
    }


# ── QBER sweep (multi-trial) ───────────────────────────────────────────────

def run_qber_sweep(
    eve_rates_pct,          # list[int], e.g. list(range(0, 101, 10))
    n_qubits: int,
    noise_rate: float,
    sample_fraction: float,
    qber_threshold: float,
    n_trials: int,
    base_seed: int,
) -> pd.DataFrame:
    """
    For each Eve rate, run n_trials independent simulations (each with a
    distinct seed = base_seed + trial) and collect QBER statistics.
    Returns a DataFrame with columns:
        eve_rate_pct, qber_mean, qber_std, qber_min, qber_max, theory
    """
    rows = []
    for rate_pct in eve_rates_pct:
        rate = rate_pct / 100.0
        qbers = []
        for t in range(n_trials):
            r = run_bb84(
                n_qubits=n_qubits,
                eve_interception_rate=rate,
                noise_rate=noise_rate,
                sample_fraction=sample_fraction,
                qber_threshold=qber_threshold,
                seed=base_seed + t,
            )
            qbers.append(r["qber_pct"])
        qbers = np.array(qbers)
        rows.append({
            "eve_rate_pct": rate_pct,
            "qber_mean":    float(qbers.mean()),
            "qber_std":     float(qbers.std()),
            "qber_min":     float(qbers.min()),
            "qber_max":     float(qbers.max()),
            "theory":       rate * 25.0,
        })
    return pd.DataFrame(rows)


# ── Detection probability sweep ────────────────────────────────────────────

def run_detection_sweep(
    k_max: int,
    n_trials: int,
    base_seed: int,
) -> pd.DataFrame:
    """
    Simulate Eve detection probability for k = 1 … k_max compared bits,
    using 100% Eve interception and 0% noise.
    Uses actual BB84 quantum functions (prepare_qubit / intercept_resend /
    measure_qubit) from bb84_simulator.py.

    For efficiency, all sifted-bit error outcomes are pre-generated in one
    loop, then sliced per k.
    """
    rng = np.random.default_rng(base_seed)
    needed = n_trials * k_max * 3  # over-generate; ~50% sifting rate

    # Collect sifted-bit error flags using the actual quantum simulation
    error_outcomes = []
    attempts       = 0
    max_attempts   = needed * 8

    while len(error_outcomes) < n_trials * k_max and attempts < max_attempts:
        alice_bit   = int(rng.integers(0, 2))
        alice_basis = rng.choice(["+", "x"])
        state       = prepare_qubit(alice_bit, alice_basis)
        state, _    = intercept_resend(state, 1.0, rng)   # 100% Eve
        bob_basis   = rng.choice(["+", "x"])
        bob_bit, _  = measure_qubit(state, bob_basis, rng)
        if alice_basis == bob_basis:                        # sifting
            error_outcomes.append(alice_bit != bob_bit)
        attempts += 1

    err_arr = np.array(error_outcomes[: n_trials * k_max], dtype=bool)
    err_mat = err_arr.reshape(n_trials, k_max)            # (trial, k_index)

    rows = []
    for k in range(1, k_max + 1):
        detected  = np.any(err_mat[:, :k], axis=1)
        sim_prob  = float(detected.mean() * 100)
        th_prob   = (1 - 0.75 ** k) * 100
        rows.append({"k": k, "sim_pct": sim_prob, "theory_pct": th_prob})

    return pd.DataFrame(rows)
