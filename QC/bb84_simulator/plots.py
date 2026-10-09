"""
plots.py
--------
Plotly chart builders for the BB84 QKD Simulator.

Colors
------
  Navy  #0B1F3A   — theory / reference lines
  Teal  #0F8B8D   — simulated data
  Coral #E4473F   — threshold / warning
"""

import plotly.graph_objects as go
import pandas as pd

NAV   = "#0B1F3A"
TEAL  = "#0F8B8D"
CORAL = "#E4473F"
BAND  = "rgba(15,139,141,0.15)"

_LAYOUT = dict(
    plot_bgcolor  = "#F7F9FF",
    paper_bgcolor = "#F7F9FF",
    font          = dict(family="Inter, sans-serif", size=12, color=NAV),
    legend        = dict(
        x=1.02, y=0.98,
        xanchor="left", yanchor="top",
        bgcolor="rgba(247,249,255,0.9)",
        bordercolor="#dce6f5", borderwidth=1,
    ),
    margin=dict(l=60, r=220, t=30, b=60),
    xaxis=dict(showgrid=True, gridcolor="#e0e8f5", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#e0e8f5", zeroline=False),
)


# ── QBER sweep chart ───────────────────────────────────────────────────────

def make_qber_sweep_chart(df: pd.DataFrame, qber_threshold_pct: float) -> go.Figure:
    """
    Multi-trial QBER vs Eve rate with mean ± std shaded band.

    df columns: eve_rate_pct, qber_mean, qber_std, theory
    """
    fig = go.Figure()

    x    = df["eve_rate_pct"].tolist()
    mean = df["qber_mean"].tolist()
    std  = df["qber_std"].tolist()
    hi   = [m + s for m, s in zip(mean, std)]
    lo   = [max(0, m - s) for m, s in zip(mean, std)]

    # Shaded ± 1 SD band
    fig.add_trace(go.Scatter(
        x       = x + x[::-1],
        y       = hi + lo[::-1],
        fill    = "toself",
        fillcolor = BAND,
        line    = dict(color="rgba(0,0,0,0)"),
        name    = "Simulated ± 1 SD",
        hoverinfo = "skip",
    ))

    # Simulated mean
    fig.add_trace(go.Scatter(
        x    = x, y = mean,
        mode = "lines+markers",
        line = dict(color=TEAL, width=2.5),
        marker = dict(size=8, color=TEAL, symbol="circle",
                      line=dict(color="white", width=1.5)),
        name = "Simulated QBER (mean)",
        hovertemplate = "Eve %{x}% → QBER %{y:.2f}%<extra></extra>",
    ))

    # Theory line
    fig.add_trace(go.Scatter(
        x    = x, y = df["theory"].tolist(),
        mode = "lines+markers",
        line = dict(color=NAV, width=2.5, dash="dash"),
        marker = dict(size=8, color=NAV, symbol="diamond",
                      line=dict(color="white", width=1.5)),
        name = "Theory: 25% × Eve rate",
        hovertemplate = "Eve %{x}% → Theory %{y:.2f}%<extra></extra>",
    ))

    # Abort threshold
    fig.add_hline(
        y                   = qber_threshold_pct,
        line                = dict(color=CORAL, width=1.8, dash="dot"),
        annotation_text     = f"Abort threshold ({qber_threshold_pct:.4g}%)",
        annotation_position = "right",
        annotation_font     = dict(color=CORAL, size=11),
    )

    layout = _LAYOUT.copy()
    layout.update(
        xaxis_title = "Eve Interception Rate (%)",
        yaxis_title = "QBER (%)",
        yaxis       = dict(range=[-1, 35], showgrid=True, gridcolor="#e0e8f5"),
        xaxis       = dict(tickvals=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                           showgrid=True, gridcolor="#e0e8f5"),
    )
    fig.update_layout(**layout)
    return fig


# ── Detection probability chart ────────────────────────────────────────────

def make_detection_chart(df: pd.DataFrame) -> go.Figure:
    """
    P(Eve detected) vs number of compared bits k.

    df columns: k, sim_pct, theory_pct
    """
    fig = go.Figure()

    # Theory
    fig.add_trace(go.Scatter(
        x    = df["k"], y = df["theory_pct"],
        mode = "lines",
        line = dict(color=NAV, width=2.5, dash="dash"),
        name = "Theory: 1 − (¾)^k",
        hovertemplate = "k=%{x} → Theory %{y:.2f}%<extra></extra>",
    ))

    # Simulated
    fig.add_trace(go.Scatter(
        x    = df["k"], y = df["sim_pct"],
        mode = "lines+markers",
        line = dict(color=TEAL, width=2.5),
        marker = dict(size=6, color=TEAL,
                      line=dict(color="white", width=1.5)),
        name = "Simulated",
        hovertemplate = "k=%{x} → Sim %{y:.2f}%<extra></extra>",
    ))

    # 99% reference
    fig.add_hline(
        y                   = 99,
        line                = dict(color=CORAL, width=1.5, dash="dot"),
        annotation_text     = "99% detection",
        annotation_position = "right",
        annotation_font     = dict(color=CORAL, size=11),
    )

    layout = _LAYOUT.copy()
    layout.update(
        xaxis_title = "Compared bits k",
        yaxis_title = "P(Eve detected) %",
        yaxis       = dict(range=[0, 102], showgrid=True, gridcolor="#e0e8f5"),
        xaxis       = dict(showgrid=True, gridcolor="#e0e8f5"),
    )
    fig.update_layout(**layout)
    return fig
