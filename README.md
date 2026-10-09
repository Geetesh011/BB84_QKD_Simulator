# BB84 Quantum Key Distribution Simulator

> A simple, correct, educational simulator for the BB84 QKD protocol.  
> Built with Python 3, NumPy, and Streamlit.  
> Does **not** use real quantum hardware or cloud quantum services.

---

## 1. Problem Statement

> *"Develop a basic simulator for Quantum Key Distribution (BB84 Protocol) to demonstrate how secure communication can be achieved using quantum principles."*

---

## 2. Objective

Demonstrate, through mathematical state-vector simulation, how:

- Alice and Bob can establish a shared secret key over a quantum channel
- Eavesdropping (Eve's intercept-resend attack) introduces detectable errors
- The Quantum Bit Error Rate (QBER) is used to detect interception
- Channel noise also contributes to QBER

---

## 3. BB84 Concept

BB84 (Bennett & Brassard 1984) uses four quantum states derived from two conjugate bases:

| Bit | Basis | State | State vector |
|-----|-------|-------|--------------|
| 0   | + (computational) | \|0⟩ | [1, 0] |
| 1   | + (computational) | \|1⟩ | [0, 1] |
| 0   | × (diagonal)      | \|+⟩ | [1/√2,  1/√2] |
| 1   | × (diagonal)      | \|−⟩ | [1/√2, −1/√2] |

**Key principle:** Measuring in the wrong basis gives a random result 50% of the time. An eavesdropper who doesn't know Alice's basis must guess, and correct guesses still collapse the state, introducing errors that Alice and Bob can detect.

---

## 4. How the Simulator Works

### Step-by-step protocol:

```
Alice
 ↓  generates n random bits and n random bases
 ↓  encodes each qubit as a 2-element state vector (BB84 state)
 ↓
[Quantum Channel]
 ↓  Eve intercepts (with configured probability) → measures → resends
 ↓  Channel noise: random bit-flip (X gate) with configured probability
 ↓
Bob
 ↓  independently chooses random bases
 ↓  measures each received qubit using Born rule
 ↓
[Public channel]
 ↓  Alice & Bob compare bases (sifting: keep matching bases only)
 ↓  Estimate QBER from a random sample of sifted bits
 ↓
Decision: QBER ≤ 11% → ACCEPT candidate key
          QBER > 11%  → ABORT (eavesdropping or noise detected)
```

### Quantum gate operations used:

```python
# Pauli-X (bit-flip) gate
X = [[0, 1],
     [1, 0]]

# Hadamard gate
H = (1/√2) * [[1,  1],
               [1, -1]]

# Qubit preparation: start with |0>
# If bit = 1: apply X  → |1>
# If basis = ×: apply H → diagonal basis state
```

### Measurement (Born rule):

- If measuring in × basis: first apply H to rotate back to computational basis
- `P(measuring 1) = |amplitude of |1⟩|²`
- Sample outcome with NumPy's RNG
- State collapses to |0⟩ or |1⟩ accordingly

---

## 5. Inputs

| Parameter | Description | Default |
|-----------|-------------|---------|
| Number of Qubits | Total qubits Alice sends | 1000 |
| Eve Interception Rate (%) | % of qubits Eve intercepts | 0% |
| Channel Noise (%) | Probability of bit-flip per qubit | 0% |
| Sample Fraction (%) | % of sifted bits used for QBER | 25% |
| Random Seed | Seed for reproducibility | 42 |
| QBER Threshold (%) | Decision boundary | 11% |

---

## 6. Outputs

- **Total qubits** — number sent by Alice
- **Sifted bits** — bits remaining after basis comparison (~50% expected)
- **Sample size** — bits used for QBER estimation
- **QBER** — estimated Quantum Bit Error Rate (%)
- **Verdict** — ACCEPT or ABORT
- **Candidate key length** — bits remaining after removing QBER sample
- **Key mismatches** — errors in the candidate key (should be 0 for ACCEPT without noise)

---

## 7. QBER Formula

```
QBER = (number of mismatched sample bits) / (number of compared sample bits)
```

Example: 16 mismatches out of 125 compared bits → QBER = 12.8%

The QBER sample is taken randomly from the sifted key. These bits are then discarded from the final candidate key (they have been revealed publicly).

---

## 8. Eve's Intercept-Resend Attack

For each intercepted qubit:
1. Eve randomly chooses a basis (+ or ×)
2. Eve measures the qubit → state collapses
3. Eve resends the collapsed (re-prepared) state to Bob

**Why this introduces errors:**
- If Eve's basis ≠ Alice's basis: Eve's measurement gives a random result (50% correct)
- Bob later measures in Alice's basis
- Incorrect Eve measurement → ~50% chance Bob gets wrong bit at that position
- After sifting (basis match), ~25% of sifted bits are errors under full interception

**Expected QBER formula:**
```
QBER_expected ≈ 25% × (Eve interception rate)
```

| Eve Rate | Expected QBER |
|----------|---------------|
| 0%       | ~0%           |
| 25%      | ~6.25%        |
| 50%      | ~12.5%        |
| 75%      | ~18.75%       |
| 100%     | ~25%          |

Actual simulated values will fluctuate around these due to finite-sample randomness.

---

## 9. Complexity

| Dimension | Complexity | Reason |
|-----------|------------|--------|
| Time      | **O(n)**   | Each of the n qubits is processed independently — one gate multiplication and one measurement per qubit. |
| Space     | **O(n)**   | We store one 2-element complex state vector per qubit. |

> **Important distinction:** This simulator processes each qubit **independently** as a 2-element state vector.  
> We are **not** simulating an n-qubit entangled state (which would require 2ⁿ complex amplitudes).  
> This keeps the implementation simple and O(n) in both time and space.

---

## 10. Limitations

- **Not real quantum hardware** — uses mathematical state-vector simulation
- **No entanglement** — qubits are independent; BB84 does not require entanglement
- **No error correction** — the candidate key is raw; real QKD applies error correction
- **No privacy amplification** — real QKD shortens the key to eliminate partial information leakage
- **No authentication** — real QKD requires an authenticated classical channel
- **No finite-key analysis** — the 11% threshold is the idealized asymptotic security threshold
- **Simplified noise model** — only random bit-flip (X gate); real channels have depolarising noise

---

## 11. How to Run

### Prerequisites

- Python 3.9 or higher
- pip

### Install dependencies

```bash
cd bb84_simulator
pip install -r requirements.txt
```

### Run the simulator

```bash
streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`.

### Quick test from command line (validation only)

```bash
python -c "
from bb84_simulator import run_bb84

# Test 1: No Eve, no noise → QBER near 0
r = run_bb84(1000, 0.0, 0.0, 0.25, 0.11, 42)
print(f'Test 1 (No Eve): QBER={r[\"qber_pct\"]:.2f}%  Verdict={r[\"verdict\"]}')

# Test 2: Full Eve → QBER near 25%
r = run_bb84(1000, 1.0, 0.0, 0.25, 0.11, 42)
print(f'Test 2 (Eve 100%): QBER={r[\"qber_pct\"]:.2f}%  Verdict={r[\"verdict\"]}')

# Test 3: Eve 50% → QBER near 12.5%
r = run_bb84(1000, 0.5, 0.0, 0.25, 0.11, 42)
print(f'Test 3 (Eve 50%): QBER={r[\"qber_pct\"]:.2f}%  Verdict={r[\"verdict\"]}')
"
```

---

## Project Structure

```
bb84_simulator/
├── app.py              # Streamlit web interface
├── bb84_simulator.py   # Core BB84 quantum simulation (NumPy)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## References

- Bennett, C. H. & Brassard, G. (1984). *Quantum cryptography: Public key distribution and coin tossing.*
- Nielsen, M. A. & Chuang, I. L. (2010). *Quantum Computation and Quantum Information.* Cambridge University Press.
- Shor, P. & Preskill, J. (2000). *Simple proof of security of the BB84 quantum key distribution protocol.* PRL 85, 441.
