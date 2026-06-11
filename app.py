import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_api_key():
    """Read API key from Streamlit secrets (cloud) or env var (local)."""
    try:
        import streamlit as st
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return os.environ.get("ANTHROPIC_API_KEY", "")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CRC Target Scout",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Design tokens ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #ffffff;
    color: #2c3340;
}

/* Force Streamlit app container background */
.stApp, .stApp > div, section.main, section.main > div, [data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
}

[data-testid="stHeader"] {
    background-color: #ffffff !important;
}

/* Remove streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #dde3ec;
}
section[data-testid="stSidebar"] * { color: #3a4252 !important; }

/* App header */
.app-header {
    border-bottom: 1px solid #dde3ec;
    padding-bottom: 1.2rem;
    margin-bottom: 1.8rem;
}
.app-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: #2a6dd9;
    letter-spacing: -0.5px;
    margin: 0;
}
.app-subtitle {
    font-size: 0.82rem;
    color: #5a6475;
    margin-top: 0.25rem;
    font-weight: 300;
    letter-spacing: 0.3px;
}
.data-badge {
    display: inline-block;
    background: #ffffff;
    border: 1px solid #c5cdd9;
    border-radius: 4px;
    padding: 2px 8px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #5a6475;
    margin-top: 0.5rem;
    margin-right: 0.3rem;
}

/* Metric cards */
.metric-card {
    background: #eef2f8;
    border: 1px solid #c8d4e4;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.8rem;
    font-weight: 600;
    color: #2a6dd9;
    line-height: 1;
}
.metric-label {
    font-size: 0.72rem;
    color: #5a6475;
    margin-top: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Section labels */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #5a6475;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 1px solid #dde3ec;
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
}

/* Gene table */
.gene-table-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #5a6475;
    text-transform: uppercase;
}

/* Pareto badge */
.pareto-badge {
    display: inline-block;
    background: rgba(88, 166, 255, 0.12);
    border: 1px solid rgba(88, 166, 255, 0.4);
    color: #2a6dd9;
    border-radius: 3px;
    padding: 1px 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    font-weight: 600;
}

/* Chat */
.chat-container {
    background: #eef2f8;
    border: 1px solid #c8d4e4;
    border-radius: 8px;
    padding: 1rem;
    max-height: 420px;
    overflow-y: auto;
}
.msg-user {
    background: #e4ecf7;
    border-radius: 6px;
    padding: 0.6rem 0.9rem;
    margin: 0.4rem 0;
    font-size: 0.85rem;
    color: #3a4252;
    border-left: 2px solid #2a6dd9;
}
.msg-ai {
    background: #ffffff;
    border-radius: 6px;
    padding: 0.6rem 0.9rem;
    margin: 0.4rem 0;
    font-size: 0.85rem;
    color: #2c3340;
    border-left: 2px solid #2ea84a;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.msg-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    color: #5a6475;
    margin-bottom: 0.2rem;
}

/* Disclaimer */
.disclaimer {
    background: rgba(210, 153, 34, 0.08);
    border: 1px solid rgba(210, 153, 34, 0.3);
    border-radius: 6px;
    padding: 0.6rem 0.9rem;
    font-size: 0.75rem;
    color: #b07a10;
    margin-top: 0.8rem;
}

/* Multiselect tags — override Streamlit default red */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: #dce6f5 !important;
    border: 1px solid #a8c0e0 !important;
    color: #2a5090 !important;
}
[data-testid="stMultiSelect"] span[data-baseweb="tag"] span {
    color: #2a5090 !important;
}
[data-testid="stMultiSelect"] span[data-baseweb="tag"] [role="presentation"] {
    color: #2a5090 !important;
}

/* Tier pills */
.tier1 { color: #d93025; font-weight: 600; }
.tier2 { color: #b07a10; font-weight: 500; }
.tier3 { color: #5a6475; }
.tier4 { color: #b0bac8; }

/* Stacked bar pathway legend */
.pathway-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Data ────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(Path(__file__).parent / "data" / "crc_targets.csv")
    return df

def compute_pareto_front(df, x_col, y_col, min_driver_strength=0.25):
    """
    True Pareto front: non-dominated set where higher driver_strength
    and more negative chronos (more essential) are both preferred.
    
    min_driver_strength: biological gate — genes below this threshold are excluded
    from Pareto candidacy. Prevents highly essential but biologically irrelevant genes
    (e.g. housekeeping genes like GAPDH, ACTB) from dominating the front.
    This is scientifically justified: a target with near-zero driver evidence
    is not a viable oncology candidate regardless of essentiality.
    Returns boolean mask.
    """
    eligible = df[x_col].values >= min_driver_strength
    xs = df[x_col].values
    ys = df[y_col].values  # more negative = better essentiality
    n = len(xs)
    dominated = np.zeros(n, dtype=bool)
    for i in range(n):
        if not eligible[i]:
            dominated[i] = True
            continue
        for j in range(n):
            if i == j or not eligible[j]:
                continue
            if xs[j] >= xs[i] and ys[j] <= ys[i] and (xs[j] > xs[i] or ys[j] < ys[i]):
                dominated[i] = True
                break
    return ~dominated

df = load_data()

# Pathway colour palette
PATHWAY_COLORS = {
    "RAS/MAPK": "#d93025",
    "WNT": "#2a6dd9",
    "WNT/Stemness": "#1a5dc0",
    "PI3K/AKT": "#b07a10",
    "TGF-β": "#7c3aed",
    "p53/Cell cycle": "#c0392b",
    "DNA damage response": "#2ea84a",
    "MMR/MSI": "#28963f",
    "RTK/RAS": "#e07b20",
    "Chromatin remodelling": "#1e6bb8",
    "Stemness": "#1a5ca8",
    "Ubiquitin/Notch": "#c49020",
    "Immune": "#208a36",
    "Metabolism": "#5a6475",
    "Housekeeping": "#b0bac8",
    "Other": "#c5cdd9"
}

TIER_LABELS = {1: "Oncogenic hotspot", 2: "Likely oncogenic", 3: "VUS", 4: "Likely neutral"}

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Filters")
    st.markdown('<div class="section-label">CMS subtype</div>', unsafe_allow_html=True)
    cms_options = ["All"] + sorted(df["cms_subtype"].unique().tolist())
    cms_filter = st.selectbox("Subtype", cms_options, index=cms_options.index("CMS2"), label_visibility="collapsed")

    st.markdown('<div class="section-label">OncoKB driver tier</div>', unsafe_allow_html=True)
    tier_filter = st.multiselect(
        "Tier", options=[1,2,3,4],
        default=[1,2,3],
        format_func=lambda x: f"Tier {x} — {TIER_LABELS[x]}",
        label_visibility="collapsed"
    )

    st.markdown('<div class="section-label">Pathway</div>', unsafe_allow_html=True)
    pathway_options = sorted(df["pathway"].unique().tolist())
    pathway_filter = st.multiselect(
        "Pathway", options=pathway_options,
        default=pathway_options,
        label_visibility="collapsed"
    )

    st.markdown('<div class="section-label">Druggability filter</div>', unsafe_allow_html=True)
    druggability_toggle = st.toggle(
        "Apply druggability filter",
        value=False,
        help="Restricts to genes with known druggable pockets (kinases, GPCRs, enzymes). "
             "Note: this systematically downranks tumour suppressors and non-enzymatic targets. "
             "Disable to see the full landscape."
    )
    if druggability_toggle:
        DRUGGABLE = {"KRAS","PIK3CA","BRAF","NRAS","EGFR","MET","ERBB2","IGF1R",
                     "FGFR1","FGFR2","WEE1","PARP1","ATR","CHK1","GSK3B","CK1A1","RAD51"}
        st.caption("⚠️ Ligand-bias active: tumour suppressors and scaffolding proteins excluded.")
    else:
        DRUGGABLE = None

    st.markdown("---")
    st.markdown('<div class="section-label">About</div>', unsafe_allow_html=True)
    st.caption(
        "⚠️ Proof-of-concept only: gene scores are synthetic, seeded from published literature "
        "to reflect realistic biological patterns (KRAS, APC, TP53 etc. scored accordingly). "
        "No live API calls are made to TCGA, DepMap, or OncoKB. "
        "The intended next step is wiring this framework to real cBioPortal/DepMap endpoints. "
        "Architecture and scoring logic are the demonstrable outputs, not the specific rankings."
    )
    st.markdown(
        '📖 [Full documentation & rationale](https://github.com/Lucia-Cordero/crc-target-scout#readme)',
        unsafe_allow_html=False
    )

# ── Filter data ─────────────────────────────────────────────────────────────────
dff = df.copy()
if cms_filter != "All":
    dff = dff[(dff["cms_subtype"] == cms_filter) | (dff["cms_subtype"] == "All")]
if tier_filter:
    dff = dff[dff["oncokb_tier"].isin(tier_filter)]
if pathway_filter:
    dff = dff[dff["pathway"].isin(pathway_filter)]
if DRUGGABLE:
    dff = dff[dff["gene"].isin(DRUGGABLE)]

# Compute Pareto front on filtered data
if len(dff) > 0:
    pareto_mask = compute_pareto_front(dff, "driver_strength", "chronos_essentiality")
    dff = dff.copy()
    dff["pareto"] = pareto_mask
else:
    pareto_mask = []
    dff["pareto"] = False

pareto_genes = dff[dff["pareto"]]["gene"].tolist()

# ── Header ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="height:4px;width:100%;border-radius:2px;overflow:hidden;margin-bottom:1.2rem;display:flex;">
  <div style="flex:1;background:#2166ac;"></div>
  <div style="flex:1;background:#4393c3;"></div>
  <div style="flex:1;background:#92c5de;"></div>
  <div style="flex:1;background:#d1e5f0;"></div>
  <div style="flex:0.5;background:#f7f7f7;"></div>
  <div style="flex:0.5;background:#fddbc7;"></div>
  <div style="flex:1;background:#f4a582;"></div>
  <div style="flex:1;background:#d6604d;"></div>
  <div style="flex:1;background:#b2182b;"></div>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<div class="app-header">
  <p class="app-title">🧬 CRC Target Scout</p>
  <p class="app-subtitle">AI-assisted target prioritisation · Colorectal Cancer (CMS2 focus)</p>
  <span class="data-badge">TCGA COAD*</span>
  <span class="data-badge">DepMap 23Q4*</span>
  <span class="data-badge">OncoKB*</span>
  <br><span style="font-size:0.68rem;color:#5a6475;margin-top:0.3rem;display:inline-block;">* representative synthetic data — no live API calls</span>
</div>
""", unsafe_allow_html=True)

# ── Metric row ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-value">{len(dff)}</div>
      <div class="metric-label">Genes in view</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-value">{sum(pareto_mask)}</div>
      <div class="metric-label">Pareto-optimal</div>
    </div>""", unsafe_allow_html=True)
with c3:
    n_t1 = len(dff[dff["oncokb_tier"]==1])
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-value">{n_t1}</div>
      <div class="metric-label">Tier 1 drivers</div>
    </div>""", unsafe_allow_html=True)
with c4:
    pathways_represented = dff[dff["pareto"]]["pathway"].nunique()
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-value">{pathways_represented}</div>
      <div class="metric-label">Pathways (Pareto)</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Main layout ──────────────────────────────────────────────────────────────────
left, right = st.columns([3, 2], gap="large")

with left:
    st.markdown('<div class="section-label">Pareto landscape — driver strength × essentiality</div>', unsafe_allow_html=True)

    # Build scatter
    colors = [PATHWAY_COLORS.get(p, "#c5cdd9") for p in dff["pathway"]]
    sizes = [16 if p else 8 for p in dff["pareto"]]
    symbols = ["diamond" if p else "circle" for p in dff["pareto"]]
    border_colors = ["#ffffff" if p else "rgba(0,0,0,0)" for p in dff["pareto"]]
    border_widths = [1.5 if p else 0 for p in dff["pareto"]]

    hover_texts = {}  # keyed by gene name — immune to index shifts after filtering
    for _, row in dff.iterrows():
        ht = (
            f"<b>{row['gene']}</b><br>"
            f"Pathway: {row['pathway']}<br>"
            f"CMS: {row['cms_subtype']}<br>"
            f"Driver strength: {row['driver_strength']:.2f}<br>"
            f"Chronos: {row['chronos_essentiality']:.2f}<br>"
            f"Log2FC: {row['log2fc_tumour_normal']:.2f}<br>"
            f"Survival HR: {row['survival_hr']:.2f}<br>"
            f"OncoKB: Tier {row['oncokb_tier']} ({TIER_LABELS[row['oncokb_tier']]})"
        )
        if row["pareto"]:
            ht += "<br><b>★ Pareto-optimal</b>"
        hover_texts[row["gene"]] = ht

    fig = go.Figure()

    # Non-pareto points
    non_pareto = dff[~dff["pareto"]]
    fig.add_trace(go.Scatter(
        x=non_pareto["driver_strength"],
        y=non_pareto["chronos_essentiality"],
        mode="markers",
        marker=dict(
            size=8,
            color=[PATHWAY_COLORS.get(p, "#c5cdd9") for p in non_pareto["pathway"]],
            opacity=0.45,
            line=dict(width=0)
        ),
        text=[hover_texts[g] for g in non_pareto["gene"]],
        hovertemplate="%{text}<extra></extra>",
        name="Other candidates",
        showlegend=False
    ))

    # Pareto points
    pareto_df = dff[dff["pareto"]]
    if len(pareto_df) > 0:
        fig.add_trace(go.Scatter(
            x=pareto_df["driver_strength"],
            y=pareto_df["chronos_essentiality"],
            mode="markers+text",
            marker=dict(
                size=14,
                color=[PATHWAY_COLORS.get(p, "#c5cdd9") for p in pareto_df["pathway"]],
                opacity=1.0,
                symbol="diamond",
                line=dict(width=1.5, color="#ffffff")
            ),
            text=pareto_df["gene"],
            textposition="top center",
            textfont=dict(size=9, color="#1a2030", family="IBM Plex Mono"),
            hovertext=[hover_texts[g] for g in pareto_df["gene"]],
            hovertemplate="%{hovertext}<extra></extra>",
            name="Pareto-optimal",
            showlegend=False
        ))

    # Reference lines
    fig.add_hline(y=-0.5, line_dash="dot", line_color="#c5cdd9", line_width=1,
                  annotation_text="essentiality threshold", annotation_font_size=9,
                  annotation_font_color="#5a6475")

    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="IBM Plex Sans", color="#2c3340", size=11),
        xaxis=dict(
            title="Driver strength (OncoKB-weighted)",
            gridcolor="#dde3ec", zerolinecolor="#c5cdd9",
            title_font=dict(size=11, color="#5a6475")
        ),
        yaxis=dict(
            title="Chronos essentiality (COAD lines) →  more essential",
            gridcolor="#dde3ec", zerolinecolor="#c5cdd9",
            title_font=dict(size=11, color="#5a6475"),
            autorange="reversed"
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        height=420,
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor="#c5cdd9",
            font=dict(family="IBM Plex Mono", size=11)
        )
    )

    # Pathway legend (manual, top-right)
    pathways_in_view = dff["pathway"].unique()
    legend_items = [(pw, PATHWAY_COLORS.get(pw, "#c5cdd9")) for pw in sorted(pathways_in_view)]
    legend_html = '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px;">'
    for pw, col in legend_items:
        legend_html += f'<span style="font-size:0.68rem;color:#5a6475;"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{col};margin-right:3px;"></span>{pw}</span>'
    legend_html += "</div>"
    st.markdown(legend_html, unsafe_allow_html=True)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div style="display:flex;gap:1.5rem;align-items:center;margin-bottom:0.6rem;flex-wrap:wrap;">
      <span style="font-size:0.72rem;color:#5a6475;">
        <span style="font-family:'IBM Plex Mono',monospace;color:#2a6dd9;">◆ diamond</span>
        &nbsp;= Pareto-optimal candidate: not dominated by any other gene on <em>both</em> driver strength and essentiality simultaneously
      </span>
      <span style="font-size:0.72rem;color:#5a6475;">
        <span style="font-family:'IBM Plex Mono',monospace;color:#5a6475;">● circle</span>
        &nbsp;= dominated on at least one axis
      </span>
    </div>
    <div style="background:rgba(210,153,34,0.08);border:1px solid rgba(210,153,34,0.3);border-radius:6px;
                padding:0.5rem 0.9rem;font-size:0.74rem;color:#b07a10;margin-bottom:0.8rem;">
      ⚠️ Pareto extremes (high driver / low essentiality or vice versa) require biological interpretation — use the AI Scientist layer.
    </div>
    """, unsafe_allow_html=True)

    # Pareto gene table
    st.markdown('<div class="section-label">Pareto-optimal candidates (★ = non-dominated on driver strength × essentiality)</div>', unsafe_allow_html=True)
    if len(pareto_df) > 0:
        display_df = pareto_df[["gene","pathway","cms_subtype","driver_strength",
                                 "chronos_essentiality","log2fc_tumour_normal",
                                 "survival_hr","oncokb_tier"]].copy()
        display_df = display_df.sort_values("driver_strength", ascending=False)
        display_df.columns = ["Gene","Pathway","CMS","Driver str.","Chronos","Log2FC","HR","Tier"]
        display_df["Driver str."] = display_df["Driver str."].round(2)
        display_df["Chronos"] = display_df["Chronos"].round(2)
        display_df["Log2FC"] = display_df["Log2FC"].round(2)
        display_df["HR"] = display_df["HR"].round(2)
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True,
            height=220
        )
    else:
        st.info("No Pareto-optimal candidates with current filters.")

with right:
    st.markdown('<div class="section-label">AI scientist — ask about a candidate</div>', unsafe_allow_html=True)

    # Gene selector
    gene_options = sorted(dff["gene"].tolist())
    pareto_first = sorted(pareto_genes) + [g for g in gene_options if g not in pareto_genes]
    selected_gene = st.selectbox(
        "Select gene to query",
        options=pareto_first,
        format_func=lambda g: f"★ {g}" if g in pareto_genes else g,
        label_visibility="collapsed"
    )

    # Gene context card
    if selected_gene:
        row = dff[dff["gene"] == selected_gene].iloc[0]
        tier_class = f"tier{int(row['oncokb_tier'])}"
        st.markdown(f"""
        <div style="background:#eef2f8;border:1px solid #c8d4e4;border-radius:8px;padding:0.9rem 1rem;margin-bottom:0.8rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
            <span style="font-family:'IBM Plex Mono',monospace;font-size:1.1rem;font-weight:600;color:#2c3340;">{selected_gene}</span>
            {'<span class="pareto-badge" title="Non-dominated on driver strength × essentiality — see graph legend">★ Pareto-optimal</span>' if selected_gene in pareto_genes else ''}
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;font-size:0.78rem;color:#5a6475;">
            <div>Pathway: <span style="color:#3a4252;">{row['pathway']}</span></div>
            <div>CMS: <span style="color:#3a4252;">{row['cms_subtype']}</span></div>
            <div>Driver str: <span style="color:#2a6dd9;font-family:'IBM Plex Mono',monospace;">{row['driver_strength']:.2f}</span></div>
            <div>Chronos: <span style="color:#2ea84a;font-family:'IBM Plex Mono',monospace;">{row['chronos_essentiality']:.2f}</span></div>
            <div>Log2FC: <span style="color:#3a4252;font-family:'IBM Plex Mono',monospace;">{row['log2fc_tumour_normal']:.2f}</span></div>
            <div>Survival HR: <span style="color:#3a4252;font-family:'IBM Plex Mono',monospace;">{row['survival_hr']:.2f}</span></div>
            <div class="{tier_class}">OncoKB Tier {int(row['oncokb_tier'])}: {TIER_LABELS[int(row['oncokb_tier'])]}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_gene" not in st.session_state:
        st.session_state.last_gene = None

    # Reset chat if gene changes
    if st.session_state.last_gene != selected_gene:
        st.session_state.messages = []
        st.session_state.last_gene = selected_gene

    # Render chat history
    chat_html = '<div class="chat-container">'
    if not st.session_state.messages:
        chat_html += '<p style="color:#b0bac8;font-size:0.8rem;text-align:center;margin-top:2rem;">Ask about this candidate\'s biology, therapeutic context, or limitations...</p>'
    for msg in st.session_state.messages:
        role_label = "You" if msg["role"] == "user" else "AI Scientist"
        role_class = "msg-user" if msg["role"] == "user" else "msg-ai"
        chat_html += f'<div class="{role_class}"><div class="msg-label">{role_label}</div>{msg["content"]}</div>'
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # Suggested prompts
    if not st.session_state.messages:
        sug_cols = st.columns(2)
        suggestions = [
            f"Why is {selected_gene} interesting in CRC?",
            f"Synthetic lethality potential for {selected_gene}?",
            f"MSI vs MSS relevance of {selected_gene}?",
            f"Key limitations of targeting {selected_gene}?",
        ]
        for i, sug in enumerate(suggestions):
            with sug_cols[i % 2]:
                if st.button(sug, key=f"sug_{i}", use_container_width=True):
                    st.session_state.pending_prompt = sug

    # Input
    col_input, col_btn = st.columns([5,1])
    with col_input:
        user_input = st.text_input(
            "Ask", placeholder=f"Ask about {selected_gene}...",
            label_visibility="collapsed", key="chat_input"
        )
    with col_btn:
        send = st.button("→", use_container_width=True)

    # Handle pending prompt from suggestion buttons
    if "pending_prompt" in st.session_state:
        user_input = st.session_state.pending_prompt
        del st.session_state.pending_prompt
        send = True

    def call_claude(messages, gene_row):
        """Call Anthropic API with gene context in system prompt."""
        gene_context = f"""
You are an AI Scientist assistant specialising in oncology target discovery, 
embedded in a CRC (colorectal cancer) target prioritisation tool.

The user is querying the gene: {gene_row['gene']}

Current data for this gene:
- Pathway: {gene_row['pathway']}
- Primary CMS subtype association: {gene_row['cms_subtype']}
- Driver strength score: {gene_row['driver_strength']:.3f} (0–1, OncoKB-weighted)
- Chronos essentiality (COAD lines): {gene_row['chronos_essentiality']:.3f} (more negative = more essential in baseline screens)
- Log2FC tumour vs normal: {gene_row['log2fc_tumour_normal']:.3f}
- Survival HR: {gene_row['survival_hr']:.3f} (>1 = worse prognosis with high expression)
- OncoKB tier: {int(gene_row['oncokb_tier'])} ({TIER_LABELS[int(gene_row['oncokb_tier'])]})
- Pareto-optimal: {gene_row['pareto']}

Important limitations to be aware of:
1. Chronos scores here are BULK averages across COAD lines — they miss context-dependent essentiality 
   (e.g. KRAS-mutant dependency on downstream effectors, MSI-high dependency on DDR)
2. CMS subtype stratification is simplified — real CRC is heterogeneous
3. Druggability annotations are ligand-biased
4. This is a proof-of-concept triage tool, not a validated pipeline

Be scientifically rigorous, concise, and honest about uncertainty. 
Highlight synthetic lethality opportunities, conditional essentiality contexts, 
and pathway redundancy where relevant. Keep responses to 3–5 sentences unless more depth is needed.
"""
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                    "x-api-key": get_api_key()
                },
                json={
                    "model": "claude-sonnet-4-5",
                    "max_tokens": 1000,
                    "system": gene_context,
                    "messages": messages
                },
                timeout=30
            )
            data = resp.json()
            if "content" not in data:
                return f"API error (status {resp.status_code}): {str(data)}"
            return data["content"][0]["text"]
        except Exception as e:
            return f"API error: {str(e)}"

    if send and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        row_data = dff[dff["gene"] == selected_gene].iloc[0]
        with st.spinner("Reasoning..."):
            reply = call_claude(
                [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                row_data
            )
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div class="disclaimer">
    ⚠️ LLM reasoning layer is context-aware but not a substitute for expert validation. 
    All biological claims should be verified against primary literature.
    </div>
    """, unsafe_allow_html=True)

# ── Validation panel ─────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Pipeline validation — known CRC targets</div>', unsafe_allow_html=True)
st.caption(
    "Sanity check: canonical CRC drivers should score highly on driver strength (blue number). "
    "If they don't, the pipeline needs recalibration. "
    "Note: Pareto status (non-dominated / dominated) is computed here on the full unfiltered dataset across all CMS subtypes — "
    "it will differ from the main graph, which computes the Pareto front only on the currently filtered subset. "
    "A gene appearing as 'dominated' here does not indicate a poor target — it may simply be outscored on both axes "
    "by another gene (e.g. APC dominated by KRAS), which is biologically expected."
)

known_targets = ["KRAS","APC","TP53","BRAF","PIK3CA","SMAD4","MLH1","MSH2","EGFR","CTNNB1"]
# Compute Pareto on full df, then filter — avoids index length mismatch
_pareto_all = compute_pareto_front(df, "driver_strength", "chronos_essentiality")
df_with_pareto = df.copy()
df_with_pareto["pareto_all"] = _pareto_all
val_df = df_with_pareto[df_with_pareto["gene"].isin(known_targets)].copy()
val_df = val_df.sort_values("driver_strength", ascending=False)

val_cols = st.columns(len(known_targets))
for i, (_, row) in enumerate(val_df.iterrows()):
    with val_cols[i]:
        pareto_str = "★" if row["pareto_all"] else "·"
        tier_color = ["#d93025","#b07a10","#5a6475","#b0bac8"][int(row["oncokb_tier"])-1]
        st.markdown(f"""
        <div style="background:#eef2f8;border:1px solid #c8d4e4;border-radius:6px;
                    padding:0.5rem;text-align:center;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:0.8rem;
                      font-weight:600;color:#2c3340;">{row['gene']}</div>
          <div style="font-size:0.65rem;color:#5a6475;margin:2px 0;" title="★ = non-dominated on driver strength × essentiality">{pareto_str} {"non-dominated" if row["pareto_all"] else "dominated"}</div>
          <div style="font-size:0.7rem;color:{tier_color};">Tier {int(row['oncokb_tier'])}</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
                      color:#2a6dd9;">{row['driver_strength']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
