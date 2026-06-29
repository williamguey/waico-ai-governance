# Inter-coder reliability (full-document consensus coding)

The principle-emphasis coding in `data/institutions.csv` is the **consensus (mean) of
four independent codings of the full source documents**, each produced by a flagship
large language model from a different developer. Coding the seven principle families
directly from the full texts (not from briefs) removes single-coder idiosyncrasy and
makes the coding reproducible; the authors reviewed every coding against the primary
sources. The source texts were assembled by `corpus_build.py` (downloads from each
instrument's official URL); the EU AI Act and the OECD Principles, whose sites block
automated download, were extracted from their official PDFs (EUR-Lex OJ L 2024/1689 and
OECD/LEGAL/0449).

**Coders (all full-document):** OpenAI GPT-5.5, Google Gemini 2.5 Pro, xAI Grok 4.3,
Anthropic Claude Opus 4.8.

**Reproduce:**
```
python corpus_build.py                                 # build corpus/ from source URLs
OPENROUTER_KEY=... python reliability_fulltext.py      # GPT-5.5, Gemini, Grok x 15 docs
OPENROUTER_KEY=... python add_claude.py                # add Claude Opus 4.8 as 4th coder
python merge_consensus.py                              # 4-coder alpha + consensus -> consensus_coding.json
python update_csv.py                                   # write consensus into data/institutions.csv
python analysis.py                                     # figures + headline quantities
```

## Reliability (interval Krippendorff's alpha)

| | alpha |
|---|---|
| Across the 4 full-document coders (105 principle judgments, 7 families) | **0.84** |
| Restricted to the 5 families in the orientation index (75 judgments) | **0.84** |
| Exact 4-way agreement | 66% |

The index-restricted alpha (0.84) matches the 7-family alpha, so the reliability does not
depend on the two families omitted from the index. Every Table 1 orientation value
reproduces exactly from Eq. (1) applied to the per-family four-coder means
(`analysis.py` derives them from `data/institutions.csv`).

Per-family alpha: sustainability 0.89, development 0.84, openness 0.77, safety 0.76,
standards 0.74, sovereignty 0.73, **rights 0.53** (rights is the hardest family to code
consistently).

## What the consensus shows

The consensus orientation index (Eq. 1) ranks the universal-membership bodies as:

| Universal body | consensus orientation | coder range |
|---|---|---|
| WAICO | **+0.88** | +0.5 to +1.0 |
| China's 2023 initiative | +0.62 | +0.5 to +1.0 |
| UN Global Dialogue | 0.00 | -0.5 to +0.5 |
| UNESCO | -0.38 | -1.0 to 0.0 |

WAICO is the most sovereignty-and-development-oriented universal-membership body, clearly
above the rights-anchored UN bodies. BRICS scores higher (+1.00) but is a closed club, not
universal. The relative ordering, WAICO and China's 2023 initiative as the only universal
bodies on the development-leaning side, is robust across all four coders.

## Robustness of the orientation index (`orientation_sensitivity.py`)

The reviewer concern that the ordering is driven by assigning "openness" to the
sovereignty/development pole is tested directly:

| Variant | universal-body order | WAICO+China top two? | rho vs paper index |
|---|---|---|---|
| V0 paper: (sov+dev+open) - (rights+safety) | WAICO, China, UN, UNESCO | yes | 1.00 |
| V1 drop openness | China, WAICO, UN, UNESCO | yes | 0.92 |
| V2 openness scored against the dev pole | China, UNESCO, UN, WAICO | no | 0.39 |

The core ordering (the two China-led instruments rank above the UN bodies) survives
dropping openness (V1). It only breaks under V2, i.e. treating open-source/open-data/
sharing as a rights-and-safety transparency norm and penalising it, which we regard as the
wrong reading. WAICO's narrow edge over China's 2023 initiative does depend on counting
openness positively.

Note: this is automated multi-model coding with human validation, not a substitute for
independent human expert coding. The per-coder codings are in `reliability_fulltext_raw.json`.
