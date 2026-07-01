# Pipeline and how to adapt this study

This repository codes a cross-section of international AI-governance instruments on three
dimensions (membership, formalization, normative orientation) and locates a focal
institution (WAICO) in the regime complex. The principle-emphasis coding is the consensus of
four flagship LLMs reading the full source documents; reliability is Krippendorff's alpha
among them. This file is the end-to-end map: research design, run order, and what to change
to run a similar study on a different topic. See `codebook.md` for per-variable definitions
and `reliability_results.md` for the reliability results.

## Research design in one paragraph

Every governance body can be described by how it admits members, how it is organized, and
what it prioritizes. We code each on those axes from its public founding document, summarize
normative orientation in a single index, and read the focal body's position against the
rest. Because the field has no ground truth, the principle coding is produced as the mean of
four independent LLM codings of the full documents and validated by the authors; the central
claim is stated as a relative ordering robust across coders, not as any single body's exact
score.

    orientation = (sovereignty + development + openness) - (rights + safety)

## Run order (each script has a docstring; run from the repo root)

1. `python corpus_build.py`
   Builds `corpus/<id>.txt` from each instrument's official URL. Two sources (EU AI Act,
   OECD Principles) block automated download and were extracted from their official PDFs by
   hand. `corpus/` is gitignored (third-party texts are not re-hosted).

2. `OPENROUTER_KEY=... python reliability_fulltext.py`
   Three flagship models (GPT-5.5, Gemini 2.5 Pro, Grok 4.3) code every instrument on the
   seven principle families from the full text, writing `reliability_fulltext_raw.json`.

3. `OPENROUTER_KEY=... python add_claude.py`
   Adds Claude Opus 4.8 as the fourth coder, same corpus and rubric, merged into the same
   JSON.

4. `python merge_consensus.py`
   Computes the four-coder consensus (mean per family) and the interval Krippendorff alpha,
   writing `consensus_coding.json`.

5. `python update_csv.py`
   Writes the consensus principle scores into `data/institutions.csv` and recomputes the
   orientation index. The structural columns (membership gate, breadth, formalization) are
   author-coded and left untouched.

6. `python analysis.py`
   Reproduces the headline quantities and both figures from `data/institutions.csv`.

Standalone checks (no API key needed):
- `python reliability_analyze.py reliability_fulltext_raw.json` prints alpha (7 families and
  the 5 index families), per-family alpha, exact agreement, and the universal-body ranking.
- `python orientation_sensitivity.py` tests how sensitive the index is to how openness is
  treated.

## Requirements

- Python 3 with pandas, numpy, matplotlib (analysis); the coding harness uses only the
  standard library (urllib, concurrent.futures).
- `OPENROUTER_KEY` for steps 2 and 3 (OpenRouter chat/completions API).
- The manuscript itself compiles with XeLaTeX (xeCJK + Fandol for the Chinese strings) and
  is not part of this data/code package.

## How to adapt this to a new topic

Reusable as-is (the machinery):
- the OpenRouter coding harness in `reliability_fulltext.py` / `add_claude.py` (the `code()`
  function, the parallel calls, the strict-JSON parsing);
- the interval Krippendorff alpha (`kalpha` in `merge_consensus.py` and `reliability_analyze.py`);
- the consensus (mean) logic and the sensitivity test.

Change these (the topic-specific parts):
- **Case list:** the `NAMES` dict (id to instrument) in `reliability_fulltext.py` and
  `add_claude.py`, and the structural rows in `data/institutions.csv` (identity, membership
  gate, breadth, formalization, source URLs).
- **Rubric:** the `RUBRIC` string (the seven principle families and their definitions) if
  your domain's dimensions differ.
- **Corpus sources:** the URL list in `corpus_build.py`.
- **Index:** the orientation formula (which families load on which pole) wherever it appears
  (`update_csv.py`, `analysis.py`, `reliability_analyze.py`, `orientation_sensitivity.py`).
- **Models:** the model ids in the two coding scripts if you want different coders.
