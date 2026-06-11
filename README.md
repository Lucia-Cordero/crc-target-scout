# CRC Target Scout

An AI-assisted target prioritisation tool for Colorectal Cancer (CRC), built as a proof-of-concept for multi-axis triage of therapeutic candidates.

## Biological rationale

CRC is not one disease — it has four consensus molecular subtypes (CMS1–4). This tool focuses on CMS2 (the most common, ~37%, WNT-driven) as its primary context, with CMS subtype annotations visible for all candidates.

### Scoring axes (intentionally separate, not composited)

| Axis | Source | Rationale |
|------|--------|-----------|
| **Driver strength** | OncoKB tier-weighted | Functional impact > raw mutation frequency; hotspot ≠ VUS |
| **Chronos essentiality** | DepMap 23Q4, COAD lines | Distinguishes overexpressed-but-dispensable genes |

A **true Pareto front** (non-dominated set) is computed across both axes — no arbitrary composite score, no quartile thresholding. A minimum driver strength gate (≥0.25) prevents highly essential but biologically irrelevant housekeeping genes from dominating.

### LLM reasoning layer

The AI Scientist chat handles what the quantitative layer can't:
- Conditional essentiality (KRAS-mutant contexts, MSI-high DDR dependency)
- Synthetic lethality reasoning
- Pathway redundancy and compensation
- Honest articulation of tool limitations

### Known limitations (by design)
- Chronos scores are bulk averages — miss context-dependent essentiality
- Druggability filter is ligand-biased (toggle off to see full landscape)
- CMS stratification is simplified
- Data is representative; production version would pull live from cBioPortal/DepMap APIs

## Running the app

```bash
pip install streamlit pandas numpy plotly requests
streamlit run app.py
```

## Validation

The pipeline is validated against canonical CRC targets (KRAS, APC, TP53, BRAF, PIK3CA, SMAD4, MLH1, MSH2) visible in the bottom panel. These should score highly — if they don't, the pipeline needs recalibration.

## Data sources
- TCGA COAD expression + survival: cBioPortal
- CRISPR essentiality: DepMap 23Q4 Chronos (COAD cell lines)
- Driver annotation: OncoKB tier classification
