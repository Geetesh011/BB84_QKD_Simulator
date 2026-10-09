"""
app.py
------
BB84 Quantum Key Distribution Simulator — Enhanced UI
Tabs: Simulation | Protocol Trace | Eve Analysis | Theory | Limitations
"""

import io
import numpy as np
import pandas as pd
import streamlit as st

from bb84_core import run_full_trace, run_qber_sweep, run_detection_sweep
from plots import make_qber_sweep_chart, make_detection_chart

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BB84 QKD Simulator",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main .block-container { padding-top: 1.2rem; max-width: 1100px; }

/* ── Hero ── */
.hero-wrap {
    background: linear-gradient(120deg, #0B1F3A 0%, #0F3A6E 100%);
    border-radius: 12px;
    padding: 22px 28px 18px;
    margin-bottom: 18px;
    color: #fff;
}
.hero-title  { font-size: 1.75rem; font-weight: 700; letter-spacing: -0.5px; color: #fff; margin:0; }
.hero-sub    { font-size: 0.95rem; color: #A8C8F0; margin: 4px 0 10px; }
.badge-edu   {
    display: inline-block;
    background: rgba(15,139,141,0.25);
    border: 1px solid #0F8B8D;
    color: #7FE0E2;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 20px;
}

/* ── Metric cards ── */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #EEF4FF 0%, #E6EEFF 100%);
    border: 1px solid #C5D5F0;
    border-radius: 10px;
    padding: 14px 18px;
    box-shadow: 0 1px 4px rgba(11,31,58,0.06);
    transition: box-shadow .2s;
}
div[data-testid="metric-container"]:hover { box-shadow: 0 3px 10px rgba(11,31,58,0.13); }
div[data-testid="metric-container"] label {
    font-size: 0.70rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.7px; color: #5a7299;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.35rem; font-weight: 700; color: #0B1F3A;
}

/* ── Verdict banners ── */
.verdict-accept, .verdict-abort {
    display: flex; align-items: center; gap: 12px;
    border-radius: 8px; padding: 13px 18px;
    font-size: 0.95rem; font-weight: 600; margin: 8px 0;
}
.verdict-accept {
    background: linear-gradient(135deg, #D4F5E2, #C5EED8);
    border: 1.5px solid #27A74A; border-left: 5px solid #27A74A; color: #0A4020;
}
.verdict-abort {
    background: linear-gradient(135deg, #FDE8EA, #FDD5D8);
    border: 1.5px solid #E4473F; border-left: 5px solid #E4473F; color: #5E1010;
}
.verdict-warn {
    background: #FFF8E1; border: 1.5px solid #F59E0B; border-left: 5px solid #F59E0B;
    border-radius: 8px; padding: 9px 16px; font-size: 0.85rem; color: #78350F; margin-top: 6px;
}

/* ── Ground truth panel ── */
.gt-panel {
    background: #F0F8FF; border: 1px solid #BDD7F5;
    border-left: 4px solid #0F8B8D; border-radius: 8px;
    padding: 14px 18px; margin: 10px 0;
}
.gt-title { font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: 0.8px; color: #0F8B8D; margin-bottom: 8px; }

/* ── Info note ── */
.info-note {
    background: #EEF6FE; border-left: 4px solid #3A8FD1;
    border-radius: 0 6px 6px 0; padding: 10px 16px;
    font-size: 0.83rem; line-height: 1.6; color: #1A3A6B; margin-top: 10px;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #F0F4FF; border-right: 1px solid #D5E0F5;
}
.sidebar-group {
    background: #fff; border: 1px solid #DCE6F5;
    border-radius: 8px; padding: 12px 14px; margin-bottom: 12px;
}
.sidebar-group-title {
    font-size: 0.70rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.8px; color: #5A7299; margin-bottom: 8px;
}

/* ── Expanders ── */
details[data-testid="stExpander"] {
    border: 1px solid #DCE6F5; border-radius: 8px;
    background: #FAFCFF; margin-bottom: 10px;
}
details[data-testid="stExpander"] summary {
    font-weight: 600; font-size: 0.88rem; color: #1A3A6B; padding: 10px 14px;
}

/* ── Theory section ── */
.theory-formula {
    background: #EEF2FF; border-left: 4px solid #0B1F3A;
    border-radius: 0 8px 8px 0; padding: 10px 16px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.92rem;
    color: #0B1F3A; margin: 8px 0;
}
.theory-card {
    background: #fff; border: 1px solid #DCE6F5;
    border-radius: 8px; padding: 14px 18px; margin-bottom: 10px;
}

/* ── Footer ── */
.footer {
    margin-top: 40px; padding-top: 14px; border-top: 1px solid #DCE6F5;
    font-size: 0.78rem; color: #8A9BB5; text-align: center;
}

/* ── Buttons ── */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0B1F3A, #1A4FA0);
    color: #fff; border: none; border-radius: 7px;
    font-weight: 600; letter-spacing: 0.3px;
    box-shadow: 0 2px 6px rgba(11,31,58,0.3);
    transition: all .2s;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #091828, #163E80);
    box-shadow: 0 4px 12px rgba(11,31,58,0.4); transform: translateY(-1px);
}

code {
    font-family: 'JetBrains Mono', monospace;
    background: #EEF2FF; color: #0B1F3A;
    padding: 1px 5px; border-radius: 4px;
}
hr { border: none; border-top: 1px solid #E0E8F5; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)


# ── Session state defaults ─────────────────────────────────────────────────
DEFAULTS = dict(
    n_qubits=1000, eve_rate=0, noise_rate=0,
    sample_pct=25, seed=42, qber_threshold=11.0,
    result=None,
    sweep_n=2000, sweep_trials=20, sweep_seed=0,
    det_k_max=30, det_trials=1000, det_seed=0,
)
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helper: apply preset ───────────────────────────────────────────────────
def apply_preset(eve, noise, n=None, sample=None, seed=None):
    st.session_state.eve_rate   = eve
    st.session_state.noise_rate = noise
    if n      is not None: st.session_state.n_qubits   = n
    if sample is not None: st.session_state.sample_pct = sample
    if seed   is not None: st.session_state.seed        = seed
    st.session_state.result = None   # clear stale results


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔐 BB84 Simulator")

    # ── Presets ────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-group-title">Presets</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    if cols[0].button("No Eve",      use_container_width=True): apply_preset(0,   0)
    if cols[1].button("Eve 50%",     use_container_width=True): apply_preset(50,  0)
    cols2 = st.columns(2)
    if cols2[0].button("Full Eve",   use_container_width=True): apply_preset(100, 0)
    if cols2[1].button("Noisy",      use_container_width=True): apply_preset(0,   5)
    if st.button("PPT settings",     use_container_width=True):
        apply_preset(0, 0, n=1000, sample=25, seed=42)
    st.divider()

    # ── Protocol ───────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-group-title">Protocol</div>', unsafe_allow_html=True)
    n_qubits = st.number_input(
        "Number of qubits", min_value=10, max_value=10000,
        value=st.session_state.n_qubits, step=100, key="n_qubits",
        help="Total qubits Alice sends. Valid range: 10–10 000."
    )
    sample_pct = st.slider(
        "QBER sample fraction (%)", 5, 50,
        value=st.session_state.sample_pct, step=5, key="sample_pct",
        help="Fraction of sifted bits used to estimate QBER."
    )

    # ── Eve ────────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-group-title">Eve (Eavesdropper)</div>',
                unsafe_allow_html=True)
    eve_rate = st.slider(
        "Interception rate (%)", 0, 100,
        value=st.session_state.eve_rate, step=1, key="eve_rate",
        help="Percentage of qubits Eve intercepts and resends."
    )

    # ── Channel ────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-group-title">Channel</div>', unsafe_allow_html=True)
    noise_rate = st.slider(
        "Noise (%)", 0, 20,
        value=st.session_state.noise_rate, step=1, key="noise_rate",
        help="Probability of a random bit-flip per qubit."
    )
    qber_threshold = st.number_input(
        "QBER abort threshold (%)", 1.0, 30.0,
        value=st.session_state.qber_threshold, step=0.5, key="qber_threshold",
    )

    # ── Seed ───────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-group-title">Seed</div>', unsafe_allow_html=True)
    seed = st.number_input(
        "Random seed", 0, 99999,
        value=st.session_state.seed, step=1, key="seed",
    )
    sc1, sc2 = st.columns(2)
    if sc1.button("Randomize", use_container_width=True):
        st.session_state.seed = int(np.random.randint(0, 99999))
        st.session_state.result = None
    if sc2.button("Reset", use_container_width=True):
        for k, v in DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()

    st.divider()
    run_clicked = st.button("▶ Run Simulation", type="primary", use_container_width=True)


# ── Hero header ────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
  <p class="hero-title">🔐 BB84 Quantum Key Distribution Simulator</p>
  <p class="hero-sub">Simulating Secure Key Establishment with Quantum Key Distribution (BB84)</p>
  <span class="badge-edu">Educational Simulator — No Real Quantum Hardware</span>
</div>
""", unsafe_allow_html=True)


# ── Run simulation ─────────────────────────────────────────────────────────
if run_clicked:
    with st.spinner("Running BB84 simulation…"):
        st.session_state.result = run_full_trace(
            n_qubits          = int(st.session_state.n_qubits),
            eve_interception_rate = st.session_state.eve_rate / 100.0,
            noise_rate        = st.session_state.noise_rate / 100.0,
            sample_fraction   = st.session_state.sample_pct / 100.0,
            qber_threshold    = st.session_state.qber_threshold / 100.0,
            seed              = int(st.session_state.seed),
        )

result = st.session_state.result


# ── Tabs ───────────────────────────────────────────────────────────────────
tab_sim, tab_trace, tab_eve, tab_theory, tab_limits = st.tabs([
    "📊 Simulation",
    "🔍 Protocol Trace",
    "👁 Eve Analysis",
    "📖 Theory",
    "⚠️ Limitations",
])


# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — SIMULATION
# ══════════════════════════════════════════════════════════════════════════
with tab_sim:
    if result is None:
        st.info("👈 Configure parameters in the sidebar and click **▶ Run Simulation**.")
        st.stop()

    # ── Metric cards ───────────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Qubits",       f"{result['n_qubits']:,}")
    c2.metric("Sifted Bits",        f"{result['n_sifted']:,}")
    c3.metric("Sample Size",        f"{result['sample_size']:,}")
    c4.metric("QBER",               f"{result['qber_pct']:.2f}%")
    c5.metric("Candidate Key Len",  f"{result['key_length']:,}")
    c6.metric("Verdict",            result["verdict"])

    # ── Verdict badge ──────────────────────────────────────────────────────
    if result["accepted"]:
        st.markdown(
            f'<div class="verdict-accept">✅ ACCEPT — Candidate shared key established '
            f'(QBER {result["qber_pct"]:.2f}% ≤ threshold {result["qber_threshold"]*100:.4g}%)</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="verdict-abort">🚨 ABORT — Eavesdropping or excessive noise detected '
            f'(QBER {result["qber_pct"]:.2f}% > threshold {result["qber_threshold"]*100:.4g}%)</div>',
            unsafe_allow_html=True,
        )

    # Extra verdict context
    eve_present = result["n_intercepted"] > 0
    if eve_present and result["accepted"]:
        st.markdown(
            '<div class="verdict-warn">⚠️ Eve was present but is <b>below the abort threshold</b> — '
            'the candidate key may still be partially compromised. '
            'Real QKD requires privacy amplification.</div>',
            unsafe_allow_html=True,
        )
    elif not eve_present and not result["accepted"]:
        st.markdown(
            '<div class="verdict-warn">ℹ️ Eve was not present — high QBER is due to channel noise. '
            'Consider a lower noise channel or higher threshold.</div>',
            unsafe_allow_html=True,
        )

    # ── Info note ──────────────────────────────────────────────────────────
    st.markdown(
        '<div class="info-note">ℹ️ The 11% threshold is used here as an idealized asymptotic BB84 '
        'security threshold for this simplified simulator, based on the idealized asymptotic BB84 '
        'security analysis. Real QKD also involves error correction, privacy amplification, '
        'authentication and finite-key analysis.</div>',
        unsafe_allow_html=True,
    )

    # ── Ground truth panel ─────────────────────────────────────────────────
    st.markdown('<div class="gt-panel">'
                '<div class="gt-title">🔭 Ground Truth Panel '
                '(simulator-only knowledge — invisible in real QKD)</div>', unsafe_allow_html=True)

    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Qubits intercepted",
              f"{result['n_intercepted']:,}",
              delta=f"{result['n_intercepted']/result['n_qubits']*100:.1f}%",
              delta_color="off")
    g2.metric("Noise flips",
              f"{result['n_noise_flipped']:,}",
              delta=f"{result['n_noise_flipped']/result['n_qubits']*100:.1f}%",
              delta_color="off")
    g3.metric("Actual error rate\n(full sifted key)",
              f"{result['actual_err_rate_pct']:.2f}%")
    g4.metric("QBER estimate\n(sampled)",
              f"{result['qber_pct']:.2f}%",
              delta=f"95% CI [{result['wilson_lo_pct']:.1f}%, {result['wilson_hi_pct']:.1f}%]",
              delta_color="off")
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption(
        "⚠️ With small samples, the QBER estimate can deviate significantly from the actual "
        "error rate. The 95% Wilson confidence interval shows the plausible range. "
        "Real QKD uses much larger samples to reduce this uncertainty."
    )

    # ── Simulation details expander ────────────────────────────────────────
    with st.expander("📋 Simulation Details", expanded=True):
        da, db = st.columns(2)
        with da:
            st.markdown("**Protocol Parameters**")
            st.write(f"- Eve interception rate: **{result['eve_interception_rate']*100:.0f}%**")
            st.write(f"- Channel noise: **{result['noise_rate']*100:.0f}%**")
            st.write(f"- Sample fraction: **{result['sample_fraction']*100:.0f}%**")
            st.write(f"- Random seed: **{result['seed']}**")
            st.markdown("**Sifting**")
            st.write(f"- Total qubits: **{result['n_qubits']:,}**")
            st.write(f"- Sifted bits: **{result['n_sifted']:,}** ({result['sifting_pct']:.1f}%)")
        with db:
            st.markdown("**QBER Analysis**")
            st.write(f"- Bits compared: **{result['sample_size']:,}**")
            st.write(f"- Mismatches: **{result['mismatches']:,}**")
            st.write(f"- QBER: **{result['qber_pct']:.2f}%**")
            st.markdown("**Candidate Key**")
            st.write(f"- Key length: **{result['key_length']:,}** bits")
            st.write(f"- Key mismatches: **{result['key_mismatches']:,}**")
            st.write(f"- Verdict: **{result['verdict']}**")

    # ── Theory vs Simulation expander ─────────────────────────────────────
    with st.expander("🔬 Theory vs Simulation", expanded=False):
        theo = result["theoretical_qber_pct"]
        actual = result["qber_pct"]
        eve_p  = result["eve_interception_rate"] * 100
        st.markdown(f"**Theoretical QBER (Eve = {eve_p:.0f}%):**  "
                    f"`25% × {eve_p:.0f}% = {theo:.2f}%`")
        st.markdown(f"**Simulated QBER:** `{actual:.2f}%`")
        if theo > 0:
            diff = abs(actual - theo)
            st.write(f"Difference: **{diff:.2f}%** — finite-sample fluctuation is expected "
                     f"(σ ≈ {(theo/100*(1-theo/100)/max(result['sample_size'],1))**0.5*100:.2f}%).")
        else:
            st.write("No Eve and no noise → theoretical QBER = 0%. "
                     "Any non-zero result is due to noise only.")

    # ── Candidate key ──────────────────────────────────────────────────────
    if result["accepted"] and result["key_length"] > 0:
        with st.expander("🔑 Candidate Shared Key (first 64 bits)", expanded=False):
            n_show = min(64, result["key_length"])
            st.markdown(f"**Alice:** `{''.join(str(b) for b in result['alice_key'][:n_show])}`")
            st.markdown(f"**Bob:**   `{''.join(str(b) for b in result['bob_key'][:n_show])}`")
            st.caption(
                f"Showing {n_show} of {result['key_length']} bits. "
                "This is a candidate key only — real QKD requires error correction "
                "and privacy amplification."
            )

    # ── Download results CSV ───────────────────────────────────────────────
    summary = {k: v for k, v in result.items()
               if k not in ("alice_key", "bob_key", "trace_df")}
    summary_df = pd.DataFrame([summary])
    csv_bytes = summary_df.to_csv(index=False).encode()
    st.download_button("⬇ Download results CSV", csv_bytes,
                       file_name="bb84_results.csv", mime="text/csv")


# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — PROTOCOL TRACE
# ══════════════════════════════════════════════════════════════════════════
with tab_trace:
    if result is None:
        st.info("Run a simulation first.")
        st.stop()

    st.subheader("Protocol Trace — Per-Qubit Walkthrough")
    st.caption(
        "Showing the first 30 qubits. Download the full trace as CSV. "
        "Colour coding: 🟥 Eve intercepted | 🟧 Noise flipped | "
        "🟩 Clean sifted bit | ⬜ Basis mismatch (discarded)"
    )

    trace_df = result["trace_df"]
    preview  = trace_df.head(30).copy()

    def colour_row(row):
        base = ""
        if row["Eve intercepted"] == "Yes":
            base = "background-color: #FFE8E8; color: #5E1010"
        elif row["Noise flipped"] == "Yes":
            base = "background-color: #FFF3E0; color: #6D3B00"
        elif row["Bases match"] == "Yes":
            base = "background-color: #E8F5E9; color: #1B5E20"
        else:
            base = "background-color: #F5F5F5; color: #555"
        return [base] * len(row)

    styled = preview.style.apply(colour_row, axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Download full trace
    full_csv = trace_df.to_csv(index=False).encode()
    st.download_button(
        f"⬇ Download full trace CSV ({len(trace_df):,} qubits)",
        full_csv, file_name="bb84_trace.csv", mime="text/csv",
    )


# ══════════════════════════════════════════════════════════════════════════
# TAB 3 — EVE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════
with tab_eve:
    st.subheader("Eve Analysis")

    # ── QBER Sweep ─────────────────────────────────────────────────────────
    st.markdown("#### QBER vs Eve Interception Rate")
    st.caption("Multi-trial sweep isolates the true relationship from single-run noise.")

    sw1, sw2, sw3 = st.columns(3)
    sweep_n      = sw1.number_input("Sweep qubits per trial", 100, 10000,
                                    st.session_state.sweep_n, 100, key="sweep_n")
    sweep_trials = sw2.number_input("Trials per Eve rate", 1, 100,
                                    st.session_state.sweep_trials, 1, key="sweep_trials")
    sweep_seed   = sw3.number_input("Base seed", 0, 99999,
                                    st.session_state.sweep_seed, 1, key="sweep_seed")
    sweep_noise  = st.session_state.noise_rate / 100.0
    sweep_thresh = st.session_state.qber_threshold / 100.0
    sweep_sample = st.session_state.sample_pct / 100.0

    @st.cache_data(show_spinner="Running sweep…")
    def cached_sweep(n, noise, sample, thresh, trials, seed):
        return run_qber_sweep(
            eve_rates_pct=list(range(0, 101, 10)),
            n_qubits=n, noise_rate=noise,
            sample_fraction=sample, qber_threshold=thresh,
            n_trials=trials, base_seed=seed,
        )

    if st.button("▶ Run QBER Sweep", key="btn_sweep"):
        sweep_df = cached_sweep(
            int(sweep_n), sweep_noise, sweep_sample, sweep_thresh,
            int(sweep_trials), int(sweep_seed),
        )
        st.plotly_chart(
            make_qber_sweep_chart(sweep_df, sweep_thresh * 100),
            use_container_width=True,
        )
        st.dataframe(sweep_df.round(2), use_container_width=True, hide_index=True)

    st.divider()

    # ── Detection probability ──────────────────────────────────────────────
    st.markdown("#### P(Eve Detected) vs Compared Bits k")
    st.caption("100% Eve interception, 0% noise. Theory: 1 − (¾)^k")

    d1, d2, d3 = st.columns(3)
    det_kmax   = d1.number_input("Max k", 5, 60, st.session_state.det_k_max, 5, key="det_k_max")
    det_trials = d2.number_input("Trials per k", 100, 5000, st.session_state.det_trials,
                                 100, key="det_trials")
    det_seed   = d3.number_input("Seed", 0, 99999, st.session_state.det_seed, 1, key="det_seed")

    @st.cache_data(show_spinner="Simulating detection probability…")
    def cached_detection(k_max, trials, seed):
        return run_detection_sweep(k_max, trials, seed)

    if st.button("▶ Run Detection Sweep", key="btn_det"):
        det_df = cached_detection(int(det_kmax), int(det_trials), int(det_seed))
        st.plotly_chart(
            make_detection_chart(det_df),
            use_container_width=True,
        )
        k15 = det_df[det_df["k"] == 15]
        if not k15.empty:
            row = k15.iloc[0]
            st.info(
                f"At **k = 15**: Simulated {row['sim_pct']:.2f}% | "
                f"Theory {row['theory_pct']:.2f}% | "
                f"Diff {abs(row['sim_pct']-row['theory_pct']):.2f} pp"
            )


# ══════════════════════════════════════════════════════════════════════════
# TAB 4 — THEORY
# ══════════════════════════════════════════════════════════════════════════
with tab_theory:
    st.subheader("Theory Reference")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="theory-card">', unsafe_allow_html=True)
        st.markdown("**Bases**")
        st.write(
            "BB84 uses two conjugate bases. Each qubit encodes one classical bit:"
        )
        st.markdown(
            "| Bit | Basis | State | Vector |\n"
            "|-----|-------|-------|---------|\n"
            "| 0   | + (rectilinear) | |0⟩ | [1, 0] |\n"
            "| 1   | + (rectilinear) | |1⟩ | [0, 1] |\n"
            "| 0   | x (diagonal)    | |+⟩ | [1/sqrt2, 1/sqrt2] |\n"
            "| 1   | x (diagonal)    | |-⟩ | [1/sqrt2, -1/sqrt2] |"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="theory-card">', unsafe_allow_html=True)
        st.markdown("**Sifting**")
        st.write(
            "Alice and Bob publicly compare which basis they used for each qubit. "
            "They keep only positions where bases agree (~50% of qubits). "
            "These form the *sifted key*."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="theory-card">', unsafe_allow_html=True)
        st.markdown("**QBER formula**")
        st.markdown(
            '<div class="theory-formula">QBER = mismatches / compared_bits</div>',
            unsafe_allow_html=True,
        )
        st.write(
            "A random sample of sifted bits is compared openly. "
            "Expected QBER with no noise and no Eve = 0%."
        )
        st.markdown(
            '<div class="theory-formula">QBER ≈ 0.25 × Eve interception rate</div>',
            unsafe_allow_html=True,
        )
        st.write(
            "Eve must guess Alice's basis (50% correct). "
            "A wrong-basis measurement re-collapses the state, "
            "introducing a 25% error rate per sifted bit."
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="theory-card">', unsafe_allow_html=True)
        st.markdown("**Detection probability**")
        st.markdown(
            '<div class="theory-formula">P(detection) = 1 − (3/4)^k</div>',
            unsafe_allow_html=True,
        )
        st.write(
            "When Eve intercepts 100%, each compared bit has a **25%** chance "
            "of being an error. Eve goes *undetected* only if ALL k bits "
            "happen to be correct — probability (3/4)^k."
        )
        st.write("Examples:")
        for k, p in [(10, 94.37), (15, 98.66), (20, 99.68), (30, 99.99)]:
            st.write(f"  • k = {k}: P(detection) ≈ **{p:.2f}%**")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("**Protocol steps:**")
    steps = [
        "Alice prepares qubits in random BB84 states",
        "(Optional) Eve intercepts and resends qubits — intercept-resend attack",
        "(Optional) Channel noise flips some qubits randomly",
        "Bob measures in random bases",
        "Alice & Bob publicly compare bases (sifting) — ~50% kept",
        "A random sample of sifted bits is compared to estimate QBER",
        "If QBER ≤ threshold → ACCEPT candidate key; else → ABORT",
    ]
    for i, s in enumerate(steps, 1):
        st.write(f"**{i}.** {s}")


# ══════════════════════════════════════════════════════════════════════════
# TAB 5 — LIMITATIONS
# ══════════════════════════════════════════════════════════════════════════
with tab_limits:
    st.subheader("Limitations of this Simulator")
    st.caption(
        "This is an educational mathematical simulator only. "
        "It does not represent a complete or production-ready QKD system."
    )

    limitations = [
        ("Ideal single qubits",
         "Each qubit is simulated as an ideal 2-element complex state vector. "
         "Real photon sources are imperfect, introduce multi-photon pulses, "
         "and suffer from channel loss."),
        ("Authenticated classical channel assumed",
         "The sifting and QBER comparison steps require an authenticated classical "
         "channel to prevent man-in-the-middle attacks. This simulator assumes "
         "authentication is in place but does not simulate it."),
        ("Intercept-resend attack only",
         "Only the intercept-resend eavesdropping strategy is modelled. "
         "Real attacks include beam-splitting, photon-number-splitting (PNS), "
         "and coherent attacks — all of which require different security proofs."),
        ("No error correction",
         "A real QKD system applies information reconciliation (e.g. Cascade protocol) "
         "to correct the residual errors in the sifted key before use. "
         "This simulator produces a raw candidate key with uncorrected errors."),
        ("No privacy amplification",
         "Eve's partial knowledge of the key must be destroyed by applying a "
         "hash function (privacy amplification). This step is not performed here."),
        ("No finite-key analysis",
         "The security threshold of 11% is an asymptotic result valid only for "
         "infinitely long keys. Finite-key corrections raise the effective threshold "
         "and reduce the secure key rate."),
        ("O(n) time/space complexity",
         "Each qubit is processed independently. "
         "Entanglement-based BB84 variants and device-independent QKD "
         "are not modelled here."),
    ]

    for title, desc in limitations:
        with st.expander(f"⚠️ {title}"):
            st.write(desc)

    st.info(
        "This simulator is intended for **educational demonstration** of the BB84 "
        "protocol's core ideas — secure sifting, QBER-based eavesdropping detection, "
        "and the quantum no-cloning theorem — not as a reference implementation."
    )

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">Developed by [Your Name] &nbsp;·&nbsp; '
    'Roll No. [Your Roll Number] &nbsp;·&nbsp; '
    'BB84 QKD Simulator &nbsp;·&nbsp; Educational Use Only</div>',
    unsafe_allow_html=True,
)
