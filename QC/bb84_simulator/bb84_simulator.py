"""
bb84_simulator.py
-----------------
Core quantum simulation for the BB84 Quantum Key Distribution protocol.

Every qubit is represented as a 2-element complex state vector.
Quantum gates are applied as 2x2 matrix multiplications.
Measurement uses the Born rule with NumPy random sampling.

Time complexity  : O(n)  – each of the n qubits is processed independently
Space complexity : O(n)  – we store one 2-element state vector per qubit
"""

import numpy as np

# ---------------------------------------------------------------------------
# Gate definitions
# ---------------------------------------------------------------------------

# |0> and |1> basis states
KET_0 = np.array([1.0 + 0j, 0.0 + 0j])
KET_1 = np.array([0.0 + 0j, 1.0 + 0j])

# Pauli-X (bit-flip) gate
X_GATE = np.array([[0, 1],
                   [1, 0]], dtype=complex)

# Hadamard gate
H_GATE = (1 / np.sqrt(2)) * np.array([[1,  1],
                                       [1, -1]], dtype=complex)


# ---------------------------------------------------------------------------
# Qubit preparation
# ---------------------------------------------------------------------------

def prepare_qubit(bit: int, basis: str) -> np.ndarray:
    """
    Prepare a BB84 qubit state vector.

    Parameters
    ----------
    bit   : 0 or 1
    basis : '+' (computational) or 'x' (diagonal)

    Returns
    -------
    state : 2-element complex NumPy array

    BB84 states:
        + basis → |0> or |1>
        x basis → |+> or |->

    Preparation logic:
        Start with |0>.
        If bit == 1  →  apply X gate   → gives |1>
        If basis == 'x'  →  apply H gate → rotates to diagonal basis
    """
    state = KET_0.copy()
    if bit == 1:
        state = X_GATE @ state      # |0> → |1>
    if basis == 'x':
        state = H_GATE @ state      # rotate to diagonal basis
    return state


# ---------------------------------------------------------------------------
# Qubit measurement
# ---------------------------------------------------------------------------

def measure_qubit(state: np.ndarray, basis: str, rng: np.random.Generator) -> tuple[int, np.ndarray]:
    """
    Measure a qubit in the given basis using the Born rule.

    Parameters
    ----------
    state : 2-element complex state vector
    basis : '+' (computational) or 'x' (diagonal)
    rng   : NumPy random Generator

    Returns
    -------
    (measured_bit, collapsed_state)

    Measurement procedure:
        If basis == 'x': first apply H to rotate into computational basis.
        Probability of measuring |1> = |amplitude_of_|1>|^2
        Sample outcome with that probability.
        Return the collapsed state corresponding to the outcome.
    """
    if basis == 'x':
        state = H_GATE @ state      # rotate diagonal → computational

    # Born rule: probability of |1> outcome
    prob_1 = float(np.abs(state[1]) ** 2)
    # Clamp floating-point rounding errors to valid range [0, 1]
    prob_1 = np.clip(prob_1, 0.0, 1.0)

    measured_bit = int(rng.random() < prob_1)
    collapsed_state = KET_1.copy() if measured_bit == 1 else KET_0.copy()
    return measured_bit, collapsed_state


# ---------------------------------------------------------------------------
# Eve – intercept-resend attack
# ---------------------------------------------------------------------------

def intercept_resend(
    state: np.ndarray,
    interception_rate: float,
    rng: np.random.Generator
) -> tuple[np.ndarray, bool]:
    """
    Eve's intercept-resend attack on a single qubit.

    Parameters
    ----------
    state            : incoming qubit state vector
    interception_rate: probability (0–1) that Eve intercepts this qubit
    rng              : NumPy random Generator

    Returns
    -------
    (outgoing_state, intercepted_flag)

    Attack logic:
        1. With probability `interception_rate`, Eve intercepts.
        2. Eve randomly chooses a basis (+ or x).
        3. Eve measures in that basis → state collapses.
        4. Eve re-prepares and resends the measured state.
        5. If Eve's basis differs from Alice's, ~50% chance of error at Bob.
    """
    if rng.random() > interception_rate:
        return state, False          # not intercepted, state passes through unchanged

    # Eve picks a random basis
    eve_basis = rng.choice(['+', 'x'])
    measured_bit, collapsed = measure_qubit(state, eve_basis, rng)
    # Eve re-prepares the qubit with her measured bit and her basis
    resent_state = prepare_qubit(measured_bit, eve_basis)
    return resent_state, True


# ---------------------------------------------------------------------------
# Channel noise
# ---------------------------------------------------------------------------

def apply_noise(state: np.ndarray, noise_rate: float, rng: np.random.Generator) -> np.ndarray:
    """
    Apply random bit-flip (X-gate) noise to a qubit.

    Parameters
    ----------
    state      : 2-element complex state vector
    noise_rate : probability (0–1) of a bit-flip occurring
    rng        : NumPy random Generator

    Returns
    -------
    Possibly flipped state vector
    """
    if rng.random() < noise_rate:
        return X_GATE @ state       # bit-flip
    return state


# ---------------------------------------------------------------------------
# Key sifting
# ---------------------------------------------------------------------------

def sift_key(
    alice_bits: list[int],
    alice_bases: list[str],
    bob_bits: list[int],
    bob_bases: list[str]
) -> tuple[list[int], list[int], list[int]]:
    """
    Sift the raw key by keeping only positions where Alice and Bob used the same basis.

    Parameters
    ----------
    alice_bits  : Alice's raw bit string
    alice_bases : Alice's basis choices
    bob_bits    : Bob's raw measured bits
    bob_bases   : Bob's basis choices

    Returns
    -------
    (sifted_alice, sifted_bob, matching_indices)
    """
    sifted_alice = []
    sifted_bob = []
    matching_indices = []

    for i, (ab, bb) in enumerate(zip(alice_bases, bob_bases)):
        if ab == bb:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_bits[i])
            matching_indices.append(i)

    return sifted_alice, sifted_bob, matching_indices


# ---------------------------------------------------------------------------
# QBER calculation
# ---------------------------------------------------------------------------

def calculate_qber(
    alice_sifted: list[int],
    bob_sifted: list[int],
    sample_fraction: float,
    rng: np.random.Generator
) -> dict:
    """
    Estimate the Quantum Bit Error Rate (QBER) from a random sample.

    QBER = (number of mismatches) / (number of compared bits)

    Parameters
    ----------
    alice_sifted    : Alice's sifted bits
    bob_sifted      : Bob's sifted bits
    sample_fraction : fraction of sifted bits to compare (e.g. 0.25 = 25%)
    rng             : NumPy random Generator

    Returns
    -------
    dict with keys:
        sample_indices, sample_size, mismatches, qber
    """
    n = len(alice_sifted)
    sample_size = max(1, int(n * sample_fraction))
    sample_indices = sorted(rng.choice(n, size=sample_size, replace=False).tolist())

    mismatches = sum(
        alice_sifted[i] != bob_sifted[i]
        for i in sample_indices
    )
    qber = mismatches / sample_size if sample_size > 0 else 0.0

    return {
        "sample_indices": sample_indices,
        "sample_size": sample_size,
        "mismatches": mismatches,
        "qber": qber,
    }


# ---------------------------------------------------------------------------
# Candidate key extraction
# ---------------------------------------------------------------------------

def extract_candidate_key(
    alice_sifted: list[int],
    bob_sifted: list[int],
    sample_indices: list[int]
) -> tuple[list[int], list[int]]:
    """
    Remove the sample bits (used for QBER) and return the remaining key bits.

    Parameters
    ----------
    alice_sifted   : Alice's full sifted key
    bob_sifted     : Bob's full sifted key
    sample_indices : indices used for QBER comparison (to be removed)

    Returns
    -------
    (alice_candidate_key, bob_candidate_key)
    """
    sample_set = set(sample_indices)
    alice_key = [b for i, b in enumerate(alice_sifted) if i not in sample_set]
    bob_key   = [b for i, b in enumerate(bob_sifted)   if i not in sample_set]
    return alice_key, bob_key


# ---------------------------------------------------------------------------
# Main BB84 runner
# ---------------------------------------------------------------------------

def run_bb84(
    n_qubits: int,
    eve_interception_rate: float,
    noise_rate: float,
    sample_fraction: float,
    qber_threshold: float,
    seed: int
) -> dict:
    """
    Run a complete BB84 QKD simulation.

    Parameters
    ----------
    n_qubits              : number of qubits Alice sends
    eve_interception_rate : fraction of qubits Eve intercepts (0–1)
    noise_rate            : probability of channel bit-flip per qubit (0–1)
    sample_fraction       : fraction of sifted key used for QBER estimate
    qber_threshold        : QBER threshold for ACCEPT/ABORT decision (e.g. 0.11)
    seed                  : random seed for reproducibility

    Returns
    -------
    dict containing all simulation results
    """
    rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------
    # Step 1 – Alice prepares random bits and random bases
    # ------------------------------------------------------------------
    alice_bits  = rng.integers(0, 2, size=n_qubits).tolist()
    alice_bases = rng.choice(['+', 'x'], size=n_qubits).tolist()

    # ------------------------------------------------------------------
    # Step 2 – Alice encodes qubits
    # ------------------------------------------------------------------
    qubit_states = [prepare_qubit(b, basis) for b, basis in zip(alice_bits, alice_bases)]

    # ------------------------------------------------------------------
    # Step 3 – Quantum channel: optional Eve intercept-resend
    # ------------------------------------------------------------------
    intercepted_flags = []
    post_eve_states = []
    for state in qubit_states:
        new_state, flag = intercept_resend(state, eve_interception_rate, rng)
        post_eve_states.append(new_state)
        intercepted_flags.append(flag)

    # ------------------------------------------------------------------
    # Step 4 – Quantum channel: optional noise (bit-flip)
    # ------------------------------------------------------------------
    post_noise_states = [apply_noise(s, noise_rate, rng) for s in post_eve_states]

    # ------------------------------------------------------------------
    # Step 5 – Bob chooses random bases and measures
    # ------------------------------------------------------------------
    bob_bases = rng.choice(['+', 'x'], size=n_qubits).tolist()
    bob_bits = []
    for state, basis in zip(post_noise_states, bob_bases):
        measured_bit, _ = measure_qubit(state, basis, rng)
        bob_bits.append(measured_bit)

    # ------------------------------------------------------------------
    # Step 6 – Sifting: keep positions where Alice and Bob used same basis
    # ------------------------------------------------------------------
    alice_sifted, bob_sifted, matching_indices = sift_key(
        alice_bits, alice_bases, bob_bits, bob_bases
    )
    n_sifted = len(alice_sifted)
    sifting_pct = (n_sifted / n_qubits * 100) if n_qubits > 0 else 0.0

    # ------------------------------------------------------------------
    # Step 7 – QBER estimation from a random sample
    # ------------------------------------------------------------------
    qber_result = calculate_qber(alice_sifted, bob_sifted, sample_fraction, rng)

    # ------------------------------------------------------------------
    # Step 8 – Security decision
    # ------------------------------------------------------------------
    qber = qber_result["qber"]
    accepted = qber <= qber_threshold
    verdict = "ACCEPT" if accepted else "ABORT"

    # ------------------------------------------------------------------
    # Step 9 – Candidate key (if accepted)
    # ------------------------------------------------------------------
    alice_key, bob_key = [], []
    key_mismatches = 0
    if accepted:
        alice_key, bob_key = extract_candidate_key(
            alice_sifted, bob_sifted, qber_result["sample_indices"]
        )
        key_mismatches = sum(a != b for a, b in zip(alice_key, bob_key))

    # ------------------------------------------------------------------
    # Preview: first 10 qubits for UI display
    # ------------------------------------------------------------------
    preview_n = min(10, n_qubits)
    preview = {
        "alice_bits":   alice_bits[:preview_n],
        "alice_bases":  alice_bases[:preview_n],
        "bob_bases":    bob_bases[:preview_n],
        "bob_bits":     bob_bits[:preview_n],
        "intercepted":  intercepted_flags[:preview_n],
    }

    return {
        # Simulation parameters
        "n_qubits":               n_qubits,
        "eve_interception_rate":  eve_interception_rate,
        "noise_rate":             noise_rate,
        "sample_fraction":        sample_fraction,
        "qber_threshold":         qber_threshold,
        "seed":                   seed,

        # Sifting results
        "n_sifted":               n_sifted,
        "sifting_pct":            sifting_pct,
        "matching_indices":       matching_indices,

        # QBER results
        "sample_size":            qber_result["sample_size"],
        "mismatches":             qber_result["mismatches"],
        "qber":                   qber,
        "qber_pct":               qber * 100,

        # Security decision
        "verdict":                verdict,
        "accepted":               accepted,

        # Candidate key
        "alice_key":              alice_key,
        "bob_key":                bob_key,
        "key_length":             len(alice_key),
        "key_mismatches":         key_mismatches,

        # Preview data for UI
        "preview":                preview,

        # Theoretical comparison
        "theoretical_qber_pct":   eve_interception_rate * 25.0,
    }
