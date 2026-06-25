# Inter-coder reliability (full-document coding)

Three flagship large language models from different developers, independent of the
author coding, each re-coded the 15 instruments on the 7 principle families **directly
from the source documents** (not from briefs). The source texts were assembled by
`corpus_build.py` (downloads from each instrument's official URL; the EU AI Act and the
OECD Principles, whose sites block automated download, use transcribed provisions, the
EU AI Act recital 1 + risk-based scheme, and the OECD five principles).

**Coders:** OpenAI GPT-5.5, Google Gemini 2.5 Pro, xAI Grok 4.3.

**Reproduce:**
```
python corpus_build.py                                 # build corpus/ from source URLs
OPENROUTER_KEY=... python reliability_fulltext.py      # 3 models x 15 docs -> reliability_fulltext_raw.json
python reliability_analyze.py reliability_fulltext_raw.json
```

## Reliability (interval Krippendorff's alpha)

| | alpha |
|---|---|
| Across the 3 LLM coders (full text) | **0.89** |
| Including the author coding as a 4th coder | 0.73 |
| Exact 3-way agreement | 80% |

Per-family alpha (3 LLM coders): development 0.94, sustainability 0.91, standards 0.88,
openness 0.84, sovereignty 0.79, safety 0.70, **rights 0.50** (rights is the hardest
family to code consistently).

## What is robust, and what is not

**Robust (relative ordering).** For every coder, WAICO and China's 2023 initiative are
the two most sovereignty-and-development-oriented universal-membership bodies, clearly
above the rights-anchored UN bodies (UN Dialogue, UNESCO). This relative finding holds
across all four coders.

**Not robust (absolute magnitude).** Reading the full texts, the independent coders
place WAICO's orientation index at about **+0.8** (range +0.5 to +1.0), versus the
author's **+2.0**. The author coding scored WAICO at the optimistic end; independent
coders read more rights/safety content in the full Action Plan. The paper therefore
frames the central result as a *relative ordering* and treats the author placement as an
upper bound; Figure 1 shows the author markers with whiskers giving the four-coder range.

Note: this is a robustness check with automated coders, not a substitute for independent
human expert coding.
