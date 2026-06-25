# Inter-coder reliability

Three flagship large language models from different developers, independent of the
original (author) coding, each re-coded the 15 instruments on the 7 principle families
from identical standardized factual briefs (the briefs are in `reliability.py`).

**Coders:** OpenAI GPT-5.5, Google Gemini 2.5 Pro, xAI Grok 4.3.

**Reproduce:**
```
OPENROUTER_KEY=... python reliability.py        # queries the three models -> reliability_raw.json
python reliability_analyze.py                    # computes alpha + headline robustness
```

## Results (interval Krippendorff's alpha)

| | alpha |
|---|---|
| Across the 3 LLM coders (15 inst x 7 families = 105 ratings) | **0.92** |
| Including the author coding as a 4th coder | 0.80 |
| Exact 3-way agreement | 82% |

Per-family alpha (3 LLM coders): safety 0.82, rights 0.88, sovereignty 1.00,
development 0.90, openness 0.91, standards 0.84, sustainability 0.91.

## Headline robustness

The orientation index = (sovereignty + development + openness) - (rights + safety) was
computed from each coder's scores. The upper-right cell (membership breadth >= 0.75 AND
orientation > 1.0) contained **exactly {WAICO, China 2023 initiative} for every coder**
(all three models and the author). The central finding is robust to the coder.

The models placed WAICO at +1.5 (vs the author's +2.0), slightly more conservative, but
still clearly at the sovereignty-and-development pole and inside the cell.

Note: the independent coders worked from standardized briefs, not the full source texts,
so the agreement reflects coding judgment given common material rather than full-text
re-coding.
