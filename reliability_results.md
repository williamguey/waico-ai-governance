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
| Across the 4 full-document coders (105 principle judgments) | **0.84** |
| Exact 4-way agreement | 66% |

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

Note: this is automated multi-model coding with human validation, not a substitute for
independent human expert coding. The per-coder codings are in `reliability_fulltext_raw.json`.
