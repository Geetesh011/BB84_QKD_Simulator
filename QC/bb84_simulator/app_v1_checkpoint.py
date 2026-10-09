"""
app.py
------
Streamlit web interface for the BB84 QKD Simulator.

Run with:
    streamlit run app.py
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

from bb84_simulator import run_bb84

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="BB84 QKD Simulator",
    page_icon="🔐",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS – polished academic design
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    /* ── Headings ── */
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.85rem;
        color: #0f2a4a;
        letter-spacing: -0.4px;
        margin-bottom: 0.2rem;
    }
    h2 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.25rem;
        color: #1a3a6b;
        letter-spacing: -0.2px;
    }
    h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1e4d8c;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: #f7f9ff;
        border-right: 1px solid #dce6f5;
    }
    section[data-testid="stSidebar"] .stMarkdown p {
        font-size: 0.82rem;
        color: #4a5568;
    }

    /* ── Metric cards ── */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #f0f5ff 0%, #e8effe 100%);
        border: 1px solid #c5d3f0;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 1px 4px rgba(26,58,107,0.06);
        transition: box-shadow 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        box-shadow: 0 3px 10px rgba(26,58,107,0.12);
    }
    div[data-testid="metric-container"] label {
        font-size: 0.73rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #5a7299;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', 'Inter', monospace;
        font-size: 1.4rem;
        font-weight: 700;
        color: #0f2a4a;
    }

    /* ── Verdict banners ── */
    .verdict-accept {
        background: linear-gradient(135deg, #d4f5e2 0%, #c8f0da 100%);
        border: 1.5px solid #27a74a;
        border-left: 5px solid #27a74a;
        border-radius: 8px;
        padding: 14px 20px;
        font-size: 1rem;
        font-weight: 600;
        color: #0e5229;
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 8px 0;
    }
    .verdict-abort {
        background: linear-gradient(135deg, #fde8ea 0%, #fddde0 100%);
        border: 1.5px solid #d93545;
        border-left: 5px solid #d93545;
        border-radius: 8px;
        padding: 14px 20px;
        font-size: 1rem;
        font-weight: 600;
        color: #6b1520;
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 8px 0;
    }

    /* ── Info note ── */
    .info-note {
        background-color: #eef6fe;
        border-left: 4px solid #3a8fd1;
        border-radius: 0 6px 6px 0;
        padding: 10px 16px;
        font-size: 0.83rem;
        line-height: 1.55;
        color: #1a3a6b;
        margin-top: 10px;
    }

    /* ── Expanders ── */
    details[data-testid="stExpander"] {
        border: 1px solid #dce6f5;
        border-radius: 8px;
        background-color: #fafcff;
        margin-bottom: 10px;
    }
    details[data-testid="stExpander"] summary {
        font-weight: 600;
        font-size: 0.9rem;
        color: #1a3a6b;
        padding: 10px 14px;
    }
    details[data-testid="stExpander"] summary:hover {
        background-color: #f0f5ff;
        border-radius: 8px;
    }

    /* ── Dataframe / tables ── */
    div[data-testid="stDataFrame"] {
        border: 1px solid #dce6f5;
        border-radius: 8px;
        overflow: hidden;
    }

    /* ── Buttons ── */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #1a4fa0, #1e5cb8);
        color: white;
        border: none;
        border-radius: 7px;
        font-weight: 600;
        letter-spacing: 0.3px;
        padding: 0.5rem 1.2rem;
        box-shadow: 0 2px 6px rgba(26,79,160,0.25);
        transition: all 0.2s;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #163f80, #1a4fa0);
        box-shadow: 0 4px 12px rgba(26,79,160,0.35);
        transform: translateY(-1px);
    }
    div[data-testid="stButton"] > button[kind="secondary"] {
        border: 1.5px solid #c5d3f0;
        border-radius: 7px;
        color: #1a3a6b;
        font-weight: 500;
        background-color: #f7f9ff;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        background-color: #eef3ff;
        border-color: #9fb5e8;
    }

    /* ── Divider ── */
    hr {
        border: none;
        border-top: 1px solid #e0e8f5;
        margin: 1rem 0;
    }

    /* ── Success / info boxes ── */
    div[data-testid="stAlert"] {
        border-radius: 8px;
        border-left-width: 4px;
    }

    /* ── Caption / small text ── */
    small, .stCaption {
        color: #6b7fa3;
        font-size: 0.8rem;
    }

    /* ── Code blocks ── */
    code {
        font-family: 'JetBrains Mono', monospace;
        background-color: #eef2ff;
        color: #1a3a6b;
        padding: 1px 5px;
        border-radius: 4px;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🔐 BB84 Quantum Key Distribution Simulator")
st.markdown(
    "<p style='font-size:1.02rem; color:#3a5a8a; margin-top:-6px; margin-bottom:2px;'>"
    "<b>Simulating Secure Key Establishment with Quantum Key Distribution (BB84)</b></p>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='font-size:0.85rem; color:#7a90b0; margin-top:0;'>"
    "Educational mathematical simulator &mdash; does not use real quantum hardware.</p>",
    unsafe_allow_html=True
)
st.divider()

# ---------------------------------------------------------------------------
# Sidebar – Inputs
# ---------------------------------------------------------------------------

st.sidebar.header("⚙️ Simulation Parameters")

n_qubits = st.sidebar.number_input(
    "Number of Qubits",
    min_value=100, max_value=10000, value=1000, step=100,
    help="Total qubits Alice sends through the quantum channel."
)

eve_rate_pct = st.sidebar.selectbox(
    "Eve Interception Rate (%)",
    options=[0, 25, 50, 75, 100],
    index=0,
    help="Percentage of qubits Eve intercepts and resends (intercept-resend attack)."
)

noise_pct = st.sidebar.selectbox(
    "Channel Noise (%)",
    options=[0, 5, 10, 15, 20],
    index=0,
    help="Probability of a random bit-flip on each qubit in the channel."
)

sample_pct = st.sidebar.slider(
    "QBER Sample Fraction (%)",
    min_value=5, max_value=50, value=25, step=5,
    help="Percentage of sifted bits used to estimate QBER."
)

seed = st.sidebar.number_input(
    "Random Seed",
    min_value=0, max_value=9999, value=42, step=1,
    help="Fixed seed for reproducibility. Seed 42 has no quantum significance."
)

qber_threshold_pct = st.sidebar.number_input(
    "QBER Threshold (%)",
    min_value=1.0, max_value=30.0, value=11.0, step=0.5,
    help="QBER <= threshold → ACCEPT; otherwise ABORT."
)

st.sidebar.divider()

run_main = st.sidebar.button("▶ Run BB84 Simulation", type="primary", use_container_width=True)
run_scenarios = st.sidebar.button("📊 Run Standard Scenarios", use_container_width=True)

# ---------------------------------------------------------------------------
# Helper: display a single simulation result
# ---------------------------------------------------------------------------

def display_result(result: dict, title: str = ""):
    if title:
        st.subheader(title)

    # --- Metric cards ---
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Qubits",      f"{result['n_qubits']:,}")
    c2.metric("Sifted Bits",       f"{result['n_sifted']:,}")
    c3.metric("Sample Size",       f"{result['sample_size']:,}")
    c4.metric("QBER",              f"{result['qber_pct']:.2f}%")
    c5.metric("Candidate Key Len", f"{result['key_length']:,}")
    c6.metric("Verdict",           result["verdict"])

    # --- Verdict banner ---
    if result["accepted"]:
        st.markdown(
            f'<div class="verdict-accept">✅ Candidate shared key accepted '
            f'(QBER = {result["qber_pct"]:.2f}% &le; threshold {result["qber_threshold"]*100:.1f}%)</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="verdict-abort">🚨 Communication aborted — eavesdropping or excessive noise detected '
            f'(QBER = {result["qber_pct"]:.2f}% &gt; threshold {result["qber_threshold"]*100:.1f}%)</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="info-note">ℹ️ The 11% threshold is used here as an idealized asymptotic BB84 security threshold '
        'for this simplified simulator. Real QKD additionally requires error correction, privacy amplification, '
        'authentication, and finite-key analysis. This is a mathematical educational simulator only.</div>',
        unsafe_allow_html=True
    )
    st.markdown("")

    # --- Simulation Details ---
    with st.expander("📋 Simulation Details", expanded=True):
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Protocol Parameters**")
            st.write(f"- Eve interception rate: **{result['eve_interception_rate']*100:.0f}%**")
            st.write(f"- Channel noise: **{result['noise_rate']*100:.0f}%**")
            st.write(f"- Sample fraction: **{result['sample_fraction']*100:.0f}%**")
            st.write(f"- Random seed: **{result['seed']}**")
            st.markdown("**Sifting**")
            st.write(f"- Total qubits: **{result['n_qubits']:,}**")
            st.write(f"- Sifted bits: **{result['n_sifted']:,}** ({result['sifting_pct']:.1f}%)")

        with col_b:
            st.markdown("**QBER Analysis**")
            st.write(f"- Bits compared: **{result['sample_size']:,}**")
            st.write(f"- Mismatches: **{result['mismatches']:,}**")
            st.write(f"- QBER: **{result['qber_pct']:.2f}%**")
            st.markdown("**Candidate Key**")
            st.write(f"- Key length: **{result['key_length']:,}** bits")
            st.write(f"- Key mismatches (remaining errors): **{result['key_mismatches']:,}**")
            st.write(f"- Verdict: **{result['verdict']}**")

    # --- Theory vs Simulation ---
    with st.expander("🔬 Theory vs Simulation", expanded=False):
        theoretical = result["theoretical_qber_pct"]
        actual = result["qber_pct"]
        eve_pct = result["eve_interception_rate"] * 100

        st.markdown(f"**Theoretical expected QBER (Eve = {eve_pct:.0f}%)**")
        st.write(f"  `QBER_theory = 25% x {eve_pct:.0f}% = {theoretical:.2f}%`")
        st.markdown(f"**Actual simulated QBER:** `{actual:.2f}%`")
        if theoretical > 0:
            diff = abs(actual - theoretical)
            st.write(
                f"  Difference: {diff:.2f}% — finite-sample fluctuations account "
                f"for deviations from the ideal 25% x interception rate relationship."
            )
        else:
            st.write(
                "  With no Eve and no noise, theoretical QBER = 0%. "
                "Any small simulated QBER is due to noise only."
            )
        st.markdown(
            "_Note: BB84 theory predicts QBER = 25% x (Eve interception rate) in expectation. "
            "A finite random simulation will fluctuate around this value._"
        )

    # --- Qubit preview table ---
    with st.expander("🔍 First 10 Qubits — Protocol Walkthrough", expanded=False):
        p = result["preview"]
        n_prev = len(p["alice_bits"])
        rows = []
        for i in range(n_prev):
            a_bit   = p["alice_bits"][i]
            a_basis = p["alice_bases"][i]
            b_basis = p["bob_bases"][i]
            b_bit   = p["bob_bits"][i]
            eve_hit = "Yes" if p["intercepted"][i] else "No"
            match   = "Match" if a_basis == b_basis else "Mismatch"
            if a_basis == b_basis:
                kept = f"{a_bit}" if a_bit == b_bit else f"{a_bit} != {b_bit}"
            else:
                kept = "discarded"
            rows.append({
                "Qubit #": i + 1,
                "Alice bit": a_bit,
                "Alice basis": a_basis,
                "Eve intercepted?": eve_hit,
                "Bob basis": b_basis,
                "Bob bit": b_bit,
                "Bases match?": match,
                "Sifted result": kept,
            })
        import pandas as pd
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # --- Candidate key display ---
    if result["accepted"] and result["key_length"] > 0:
        with st.expander("🔑 Candidate Shared Key (first 64 bits)", expanded=False):
            display_len = min(64, result["key_length"])
            alice_display = "".join(str(b) for b in result["alice_key"][:display_len])
            bob_display   = "".join(str(b) for b in result["bob_key"][:display_len])
            st.markdown(f"**Alice's candidate key:** `{alice_display}`")
            st.markdown(f"**Bob's candidate key:**   `{bob_display}`")
            st.caption(
                f"Showing {display_len} of {result['key_length']} bits. "
                "This is a candidate key only — not a final cryptographic key. "
                "Real QKD requires error correction and privacy amplification."
            )


# ---------------------------------------------------------------------------
# QBER vs Eve graph  (enhanced matplotlib style)
# ---------------------------------------------------------------------------

def plot_qber_vs_eve(n_qubits: int, noise_rate: float, sample_fraction: float,
                     qber_threshold: float, seed: int) -> plt.Figure:
    """
    Plot observed QBER vs Eve interception rate alongside the theoretical line.
    """
    eve_rates = [0, 0.25, 0.50, 0.75, 1.00]
    observed_qbers = []

    for er in eve_rates:
        res = run_bb84(
            n_qubits=n_qubits,
            eve_interception_rate=er,
            noise_rate=noise_rate,
            sample_fraction=sample_fraction,
            qber_threshold=qber_threshold,
            seed=seed,
        )
        observed_qbers.append(res["qber_pct"])

    theoretical_qbers = [er * 25.0 for er in eve_rates]
    eve_pcts = [er * 100 for er in eve_rates]

    # ── Polished matplotlib style ──
    fig, ax = plt.subplots(figsize=(8, 4.2))
    fig.patch.set_facecolor("#fafcff")
    ax.set_facecolor("#fafcff")

    ax.plot(
        eve_pcts, theoretical_qbers,
        color="#1a4fa0", linestyle="--", marker="o",
        linewidth=2.2, markersize=7, markerfacecolor="white",
        markeredgewidth=2, markeredgecolor="#1a4fa0",
        label="Theoretical  (25% × Eve rate)"
    )
    ax.plot(
        eve_pcts, observed_qbers,
        color="#d93545", linestyle="-", marker="s",
        linewidth=2.2, markersize=7, markerfacecolor="white",
        markeredgewidth=2, markeredgecolor="#d93545",
        label="Simulated QBER"
    )
    ax.axhline(
        y=qber_threshold * 100,
        color="#e07b00", linestyle=":", linewidth=1.8,
        label=f"Security Threshold ({qber_threshold*100:.4g}%)"
    )

    ax.fill_between(eve_pcts, theoretical_qbers, observed_qbers,
                    alpha=0.07, color="#1a4fa0")

    ax.set_xlabel("Eve Interception Rate (%)", fontsize=12, color="#1a3a6b", labelpad=8)
    ax.set_ylabel("QBER (%)",                  fontsize=12, color="#1a3a6b", labelpad=8)
    ax.set_title("BB84 — QBER vs Eve Interception Rate",
                 fontsize=13, fontweight="bold", color="#0f2a4a", pad=12)

    ax.legend(fontsize=10, framealpha=0.9, edgecolor="#dce6f5",
              fancybox=True, loc="upper left")

    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_ylim(-1, 32)
    ax.tick_params(colors="#4a5568", labelsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#dce6f5")
    ax.spines["bottom"].set_color("#dce6f5")
    ax.grid(True, linestyle="--", alpha=0.35, color="#c5d3f0")

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Standard scenarios
# ---------------------------------------------------------------------------

STANDARD_SCENARIOS = [
    {"name": "1. No Eve",    "eve": 0.00, "noise": 0.00},
    {"name": "2. Eve 25%",   "eve": 0.25, "noise": 0.00},
    {"name": "3. Eve 50%",   "eve": 0.50, "noise": 0.00},
    {"name": "4. Eve 100%",  "eve": 1.00, "noise": 0.00},
    {"name": "5. Noise 5%",  "eve": 0.00, "noise": 0.05},
    {"name": "6. Noise 15%", "eve": 0.00, "noise": 0.15},
]


def run_standard_scenarios(n_qubits, sample_fraction, qber_threshold, seed):
    import pandas as pd
    rows = []
    results = []
    for sc in STANDARD_SCENARIOS:
        res = run_bb84(
            n_qubits=n_qubits,
            eve_interception_rate=sc["eve"],
            noise_rate=sc["noise"],
            sample_fraction=sample_fraction,
            qber_threshold=qber_threshold,
            seed=seed,
        )
        rows.append({
            "Scenario":    sc["name"],
            "Eve (%)":     f"{sc['eve']*100:.0f}%",
            "Noise (%)":   f"{sc['noise']*100:.0f}%",
            "Sifted Bits": res["n_sifted"],
            "Sample Size": res["sample_size"],
            "QBER (%)":    f"{res['qber_pct']:.2f}%",
            "Key Errors":  res["key_mismatches"],
            "Verdict":     res["verdict"],
        })
        results.append(res)
    return pd.DataFrame(rows), results


# ---------------------------------------------------------------------------
# Main – Run simulation on button click
# ---------------------------------------------------------------------------

if run_main:
    with st.spinner("Running BB84 simulation..."):
        result = run_bb84(
            n_qubits=int(n_qubits),
            eve_interception_rate=eve_rate_pct / 100.0,
            noise_rate=noise_pct / 100.0,
            sample_fraction=sample_pct / 100.0,
            qber_threshold=qber_threshold_pct / 100.0,
            seed=int(seed),
        )

    st.success("Simulation complete.")
    st.header("📊 Simulation Results")
    display_result(result)

    # QBER vs Eve graph
    st.subheader("📈 QBER vs Eve Interception Rate")
    fig = plot_qber_vs_eve(
        n_qubits=int(n_qubits),
        noise_rate=noise_pct / 100.0,
        sample_fraction=sample_pct / 100.0,
        qber_threshold=qber_threshold_pct / 100.0,
        seed=int(seed),
    )
    st.pyplot(fig)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Standard scenarios
# ---------------------------------------------------------------------------

if run_scenarios:
    with st.spinner("Running all standard scenarios..."):
        df_scenarios, scenario_results = run_standard_scenarios(
            n_qubits=int(n_qubits),
            sample_fraction=sample_pct / 100.0,
            qber_threshold=qber_threshold_pct / 100.0,
            seed=int(seed),
        )

    st.header("📊 Standard Scenario Results")
    st.caption(
        "All values are generated by actual simulation. "
        "Results may differ from illustrative PPT numbers — genuine simulation output is used."
    )

    # Colour-code verdicts
    def highlight_verdict(val):
        if val == "ACCEPT":
            return "background-color: #d4f5e2; color: #0e5229; font-weight: 600"
        elif val == "ABORT":
            return "background-color: #fde8ea; color: #6b1520; font-weight: 600"
        return ""

    styled = df_scenarios.style.applymap(highlight_verdict, subset=["Verdict"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Individual expandable results
    for sc_name, res in zip([s["name"] for s in STANDARD_SCENARIOS], scenario_results):
        with st.expander(f"Details — {sc_name}", expanded=False):
            display_result(res)


# ---------------------------------------------------------------------------
# Footer / Info when nothing has been run yet
# ---------------------------------------------------------------------------

if not run_main and not run_scenarios:
    st.info(
        "👈 **Configure parameters in the sidebar** and click **Run BB84 Simulation** to start.\n\n"
        "Or click **Run Standard Scenarios** to see results for six pre-defined test cases at once."
    )

    st.subheader("ℹ️ About BB84")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            "**BB84 states used in this simulator:**\n\n"
            "| Bit | Basis | State | Vector |\n"
            "|-----|-------|-------|--------|\n"
            "| 0   | +     | 0-ket  | [1, 0] |\n"
            "| 1   | +     | 1-ket  | [0, 1] |\n"
            "| 0   | x     | plus-ket  | [1/sqrt2, 1/sqrt2] |\n"
            "| 1   | x     | minus-ket | [1/sqrt2, -1/sqrt2] |\n\n"
            "**QBER formula:**\n\n"
            "```\nQBER = mismatches / compared_bits\n```\n\n"
            "**Security threshold:** QBER <= 11% => ACCEPT\n"
        )
    with col2:
        st.markdown("""
**Protocol steps:**
1. Alice prepares qubits in random BB84 states
2. (Optional) Eve intercepts and resends qubits
3. (Optional) Channel noise flips some qubits
4. Bob measures in random bases
5. Alice & Bob publicly compare bases (sifting)
6. QBER is estimated from a random sample
7. If QBER <= 11%, the candidate key is accepted

**Why Eve introduces errors:**
- Eve must guess Alice's basis (50% chance correct)
- Wrong basis measurement collapses the state randomly
- ~25% of sifted bits become errors under full interception

**Complexity:**
- Time: O(n) — each qubit processed independently
- Space: O(n) — one 2-element state vector per qubit
""")
