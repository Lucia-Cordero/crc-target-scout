# CRC Target Scout

> ⚠️ **Proof-of-concept only.** Gene scores are synthetic, seeded from published literature to reflect realistic biological patterns. No live API calls are made to TCGA, DepMap, or OncoKB. Specific rankings should not be interpreted as real results. The architecture, scoring framework, and LLM reasoning layer are the demonstrable outputs.

An AI-assisted target prioritisation framework for Colorectal Cancer (CRC), prototyping a multi-axis triage workflow for therapeutic candidates.

> This prototype was developed with the assistance of Claude (Anthropic) for code generation. The biological rationale, scoring design decisions, and critical review of limitations are the author's own.

---

## The problem this addresses

Drug discovery in oncology starts with an uncomfortable reality: there are thousands of genes dysregulated in any given tumour, but only a handful will ever make viable therapeutic targets. The challenge is not finding candidates — it is narrowing them down intelligently.

Naïve approaches fail in predictable ways:

- **Overexpression alone is insufficient.** Many genes are highly expressed in tumours but are entirely dispensable — collateral noise rather than drivers. A target that is overexpressed but not essential to tumour survival will not respond to inhibition.
- **Mutation frequency is misleading without functional context.** A variant of unknown significance (VUS) at high frequency is not the same as a recurrent oncogenic hotspot. Raw mutation counts conflate these.
- **Bulk essentiality screens miss the most interesting targets.** The best oncology targets are often not essential in baseline CRISPR screens — synthetic lethality targets, pathway bottlenecks, and context-dependent dependencies (e.g. KRAS-mutant tumours relying on downstream effectors) appear as moderate scores in bulk data. They require context-aware interpretation.
- **Single-gene ranking ignores pathway biology.** Ranking EGFR highly without acknowledging RAS pathway compensation mechanisms produces leads that fail in practice.
- **Cancer is not one disease.** In CRC specifically, the four consensus molecular subtypes (CMS1–4) have distinct driver landscapes, immune contexts, and therapeutic vulnerabilities. A target prioritisation that averages across all subtypes produces a biologically diluted ranking that is meaningful for none of them.

---

## Approach

CRC Target Scout is a minimal working prototype that attempts to address the most tractable of these challenges within a one-day build constraint.

### Scoring framework — axes intentionally separate, not composited

Rather than collapsing multiple signals into a single weighted score (which introduces arbitrary weighting decisions and obscures trade-offs), the tool maintains two independent axes and computes a **true Pareto front** — the set of genes not dominated by any other gene on both dimensions simultaneously.

| Axis | Intended source | Design rationale |
|------|----------------|-----------------|
| Driver strength | OncoKB tier-weighted | Prioritises functional impact over raw frequency; oncogenic hotspots weighted above VUS |
| Chronos essentiality | DepMap 23Q4, COAD lines | Filters overexpressed-but-dispensable genes; identifies genuine dependencies |

A minimum driver strength gate (≥0.25) prevents highly essential but biologically irrelevant housekeeping genes (GAPDH, ACTB etc.) from dominating the Pareto front — a real artefact of bulk CRISPR screens.

### CMS subtype stratification

The tool defaults to CMS2 (the most common subtype, ~37%, canonically WNT-driven) rather than averaging across all subtypes. This is a deliberate biological decision: a ranking averaged across CMS1–4 is meaningful for none of them. CMS annotations are visible for all candidates and the filter is user-adjustable.

### LLM reasoning layer

The quantitative layer handles triage. The AI Scientist chat layer handles interpretation — the things that resist discretisation:

- Conditional essentiality (KRAS-mutant dependency on downstream effectors; MSI-high DDR pathway vulnerabilities)
- Synthetic lethality potential
- Pathway redundancy and compensation mechanisms
- Context-specific safety and translational considerations

This architecture mirrors the intended design of tools like Owkin K: a scoring layer to reduce the candidate space, with an LLM reasoning layer for biological context that rigid scoring cannot capture.

---

## Known limitations and future directions

Many of the most important considerations are acknowledged but out of scope for this prototype:

| Limitation | Impact | Intended fix |
|------------|--------|--------------|
| Synthetic data | Rankings are illustrative, not real | Wire to live cBioPortal + DepMap APIs |
| Bulk Chronos scores | Miss conditional essentiality (KRAS-mut, MSI-high) | Stratified DepMap queries by genetic context |
| Simplified CMS stratification | Real CRC heterogeneity is greater | Full CMS classifier on TCGA samples |
| Druggability filter is ligand-biased | Systematically downranks tumour suppressors, scaffolding proteins | Replace with structure-based druggability scores |
| Single composite Pareto | Ignores pathway-level redundancy | Pathway-aware scoring; penalise candidates in redundant pathway nodes |
| No translational or safety layer | Clinical attrition not modelled | Integrate clinical trial outcome data, toxicity flags |
| No multi-omics integration | Expression + mutation only | Add CNV, methylation, proteomics axes |

---

## Validation

The pipeline is validated against canonical CRC targets (KRAS, APC, TP53, BRAF, PIK3CA, SMAD4, MLH1, MSH2) in the bottom panel. These should score highly on driver strength — if they don't, the pipeline needs recalibration. Pareto status will vary by filter context, which is expected and explained in the UI.

---

## Running locally

```bash
pip install streamlit pandas numpy plotly requests python-dotenv
streamlit run app.py
```

Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=sk-ant-...
```

## Intended data sources (not yet live)
- TCGA COAD expression + survival: cBioPortal REST API
- CRISPR essentiality: DepMap 23Q4 Chronos (COAD cell lines)
- Driver annotation: OncoKB tier classification
