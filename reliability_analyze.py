"""Compute inter-coder reliability (Krippendorff's alpha, interval) across the three
flagship LLM coders, and test whether the headline finding survives independent coding."""
import json, csv, itertools

PRIN = ["safety", "rights", "sovereignty", "development", "openness", "standards", "sustainability"]
raw = json.load(open("reliability_raw.json"))
coders = list(raw.keys())
insts = list(next(iter(raw.values())).keys())

# author coding from the dataset
author = {}
_col = {"openness": "open"}  # dataset column is p_open
for r in csv.DictReader(open("data/institutions.csv", encoding="utf-8")):
    author[r["inst_id"]] = {p: float(r["p_" + _col.get(p, p)]) for p in PRIN}

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
        Do_num += pair  # (1/(m-1)) * 2 * pair / 2 = pair, for m=3
        n += m
    Do = Do_num / n
    return 1 - Do / De if De else float("nan")

# overall alpha across the 3 LLM coders: units = each (inst, principle)
units_all = [[raw[c][i][p] for c in coders] for i in insts for p in PRIN]
print("=== Inter-coder reliability across 3 flagship LLMs (interval Krippendorff alpha) ===")
print(f"Overall alpha (15 inst x 7 principles = {len(units_all)} units, 3 coders): {kalpha_interval(units_all):.3f}")
print("Per-principle alpha:")
for p in PRIN:
    u = [[raw[c][i][p] for c in coders] for i in insts]
    print(f"  {p:13s}: {kalpha_interval(u):.3f}")

# exact agreement rate
agree = sum(len(set(u)) == 1 for u in units_all) / len(units_all)
print(f"Exact 3-way agreement: {agree*100:.0f}% of {len(units_all)} ratings")

# include author as a 4th coder
units_4 = [[raw[c][i][p] for c in coders] + [author[i][p]] for i in insts for p in PRIN]
print(f"Alpha incl. author coding (4 coders): {kalpha_interval(units_4):.3f}")

# orientation index per coder; headline test
def orient(d): return (d["sovereignty"] + d["development"] + d["openness"]) - (d["rights"] + d["safety"])
print("\n=== Orientation index per coder; does WAICO stay at the development pole? ===")
breadth = {r["inst_id"]: float(r["breadth"]) for r in csv.DictReader(open("data/institutions.csv", encoding="utf-8"))}
hdr = f"{'inst':13s} " + " ".join(f"{c.split('/')[1][:9]:>9s}" for c in coders) + f"{'author':>9s}"
print(hdr)
cell_ok = []
for i in insts:
    vals = [orient(raw[c][i]) for c in coders]
    a = orient(author[i])
    print(f"{i:13s} " + " ".join(f"{v:>9.1f}" for v in vals) + f"{a:>9.1f}")
# cell occupancy per coder: universal (breadth>=0.75) AND orientation>1
print("\nUpper-right cell (breadth>=0.75 AND orientation>1.0) per coder:")
for c in coders + ["author"]:
    src = author if c == "author" else raw[c]
    occ = [i for i in insts if breadth[i] >= 0.75 and orient(src[i]) > 1.0]
    print(f"  {c.split('/')[-1]:18s}: {occ}")
