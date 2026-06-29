"""Compute inter-coder reliability (Krippendorff's alpha, interval) across the flagship
LLM coders that code the instruments from the full source documents, and report the
consensus orientation ranking that is the paper's headline. The dataset coding
(data/institutions.csv) is the mean of these coders, so it is not added as a separate
coder here.

Usage: python reliability_analyze.py [reliability_fulltext_raw.json]
"""
import json, csv, itertools, sys

PRIN = ["safety", "rights", "sovereignty", "development", "openness", "standards", "sustainability"]
raw = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "reliability_fulltext_raw.json"))
coders = list(raw.keys())
insts = list(next(iter(raw.values())).keys())

def kalpha_interval(units):
    # units: list of lists of ratings (one list per coded unit)
    allv = [v for u in units for v in u]
    N = len(allv)
    s2 = sum(v * v for v in allv); s1 = sum(allv)
    sum_sq_pairs = 2 * N * s2 - 2 * s1 * s1            # sum_{i,j}(vi-vj)^2
    De = sum_sq_pairs / (N * (N - 1))
    Do_num = 0.0; n = 0
    for u in units:
        m = len(u)
        if m < 2: continue
        pair = sum((a - b) ** 2 for a, b in itertools.combinations(u, 2))
        Do_num += 2 * pair / (m - 1)   # ordered coder pairs: 2x the unordered sum
        n += m
    Do = Do_num / n
    return 1 - Do / De if De else float("nan")

units_all = [[raw[c][i][p] for c in coders] for i in insts for p in PRIN]
INDEX = ["safety", "rights", "sovereignty", "development", "openness"]  # families in the orientation index
units_idx = [[raw[c][i][p] for c in coders] for i in insts for p in INDEX]
print(f"=== Inter-coder reliability across {len(coders)} full-document LLM coders ===")
print("Coders:", ", ".join(c.split("/")[-1] for c in coders))
print(f"Overall alpha (15 inst x 7 principles = {len(units_all)} units): {kalpha_interval(units_all):.3f}")
print(f"Index-family alpha (5 families x 15 = {len(units_idx)} units): {kalpha_interval(units_idx):.3f}")
print("Per-principle alpha:")
for p in PRIN:
    u = [[raw[c][i][p] for c in coders] for i in insts]
    print(f"  {p:13s}: {kalpha_interval(u):.3f}")
agree = sum(len(set(u)) == 1 for u in units_all) / len(units_all)
print(f"Exact {len(coders)}-way agreement: {agree*100:.0f}% of {len(units_all)} ratings")

def orient(d): return (d["sovereignty"] + d["development"] + d["openness"]) - (d["rights"] + d["safety"])
breadth = {r["inst_id"]: float(r["breadth"]) for r in csv.DictReader(open("data/institutions.csv", encoding="utf-8"))}

print("\n=== Consensus orientation, universal-membership bodies (breadth >= 0.75) ===")
uni = sorted((i for i in insts if breadth[i] >= 0.75),
             key=lambda i: -sum(orient(raw[c][i]) for c in coders) / len(coders))
for i in uni:
    os_ = [orient(raw[c][i]) for c in coders]
    mean = sum(os_) / len(os_)
    print(f"  {i:13s} consensus {mean:+.2f}  (coder range {min(os_):+.1f} to {max(os_):+.1f})")
