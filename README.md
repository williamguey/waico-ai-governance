# WAICO and the Global AI Governance Regime Complex: Data and Code

Replication data and code for the paper:

> **World Artificial Intelligence Cooperation Organization (WAICO): Mapping an Emerging Institution in the Global AI Governance Regime Complex**
> William Guey, Wei Zhang, Vitor D. de Moura, Pierrick Bougault, José O. Gomes.

The manuscript itself is available as a preprint on arXiv. This repository holds only the data, analysis code, and figures needed to reproduce the results. The paper places the proposed World Artificial Intelligence Cooperation Organization (WAICO, 世界人工智能合作组织) within the emerging regime complex for AI by coding a representative set of fifteen international AI governance instruments and institutions on how they admit members, how they are organized, and what they prioritize.

## Contents

| File | Description |
|------|-------------|
| `data/institutions.csv` | The coded dataset: 15 instruments and institutions, one row each, with the public source URL for every row. |
| `analysis.py` | Reproduces all reported quantities and both figures from the dataset. |
| `figures/` | `fig1_map.{png,pdf}` (normative orientation vs membership breadth) and `fig2_definedness.{png,pdf}` (institutional formalization). |
| `corpus_build.py` | Assembles the source-document corpus from each instrument's official URL (the corpus itself is not re-hosted). |
| `reliability_fulltext.py`, `add_claude.py` | Coding harness: four flagship LLMs (GPT-5.5, Gemini 2.5 Pro, Grok 4.3, Claude Opus 4.8) code the 15 instruments from the full source documents via OpenRouter. Needs `OPENROUTER_KEY`. |
| `reliability_fulltext_raw.json` | The four models' raw full-text codings. |
| `merge_consensus.py`, `consensus_coding.json` | Builds the four-coder consensus (mean), computes Krippendorff's alpha, and writes the per-institution orientation range. The consensus is the principle coding used in the dataset. |
| `update_csv.py` | Writes the consensus principle scores into `data/institutions.csv`. |
| `reliability_analyze.py` | Standalone Krippendorff's alpha across coders (`python reliability_analyze.py reliability_fulltext_raw.json`). |
| `orientation_sensitivity.py` | Sensitivity of the orientation index to how `openness` is treated (drop it / score it against the development pole). |
| `reliability_results.md` | Summary (four-coder full-text alpha = 0.84; relative ordering robust across coders). |

## Reproducing the analysis

Requires Python 3 with `pandas`, `numpy`, and `matplotlib`.

```bash
python analysis.py
```

This prints the summary statistics and writes the figures to `figures/`.

The full coding pipeline (corpus assembly, four-model coding, consensus, reliability) and a guide to adapting the study to a new topic are in [`PIPELINE.md`](PIPELINE.md); per-variable coding definitions are in the coding manual.

## Dataset columns

`institutions.csv` codes each institution on three groups of variables.

**Identity:** `inst_id`, `name`, `lead_actor`, `year`, `status` (operating or proposed).

**Membership logic:** `entry_condition` (values-gated, capability-gated, regional, universal-open); `values_gate` (founding text conditions entry on shared values); `accession_normative_test` (accession requires meeting a normative criterion); `open_to_all` (describes itself as open to any state); `global_south_priority` (bridging the global divide is an organizing goal).

**Design and orientation:** `function`, `orientation` (regulatory or distributive), `development_orientation` (0–2), `legal_force`, `definedness` (0–5: charter, secretariat, budget, voting rules, defined membership). Principle emphasis is coded on a 0/0.5/1 scale across seven families (`p_safety`, `p_rights`, `p_sovereignty`, `p_development`, `p_open`, `p_standards`, `p_sustainability`); each value is the mean of four flagship LLMs coding the full source document (see the reliability files). Two summary indices are derived: `norm_orientation` (negative = rights and safety; positive = sovereignty and development) and `breadth` (0 = club, 1 = universal).

**Provenance:** `source_url` records the public primary source from which each institution was coded.

## Sources

Every institution is coded from a public primary source (the founding treaty, official statement, or constitutive document), whose URL is recorded in the `source_url` column of the dataset.

## License

The dataset is released under CC BY 4.0 and the code under the MIT License, for replication and reuse.
