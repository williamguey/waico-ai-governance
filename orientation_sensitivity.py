"""Sensitivity of the normative-orientation index to how 'openness' is treated.
Reviewer concern: openness is assigned to the sovereignty/development pole, but could
plausibly load with rights/safety (transparency). Test whether the ordering survives.

Variants (using the 4-coder consensus means):
  V0  paper index:        (sov + dev + open) - (rights + safety)
  V1  drop openness:      (sov + dev)        - (rights + safety)
  V2  openness penalised: (sov + dev)        - (rights + safety + open)
"""
import json, csv

cons = json.load(open("consensus_coding.json"))
breadth = {r["inst_id"]: float(r["breadth"]) for r in csv.DictReader(open("data/institutions.csv", encoding="utf-8"))}
m = {i: cons[i]["means"] for i in cons}

def v0(s): return (s["sovereignty"] + s["development"] + s["openness"]) - (s["rights"] + s["safety"])
def v1(s): return (s["sovereignty"] + s["development"]) - (s["rights"] + s["safety"])
def v2(s): return (s["sovereignty"] + s["development"]) - (s["rights"] + s["safety"] + s["openness"])
variants = {"V0 paper": v0, "V1 drop open": v1, "V2 open penalised": v2}

def spearman(a, b):
    ra = {k: r for r, k in enumerate(sorted(a, key=lambda k: a[k]))}
    rb = {k: r for r, k in enumerate(sorted(b, key=lambda k: b[k]))}
    n = len(a); d2 = sum((ra[k] - rb[k]) ** 2 for k in a)
    return 1 - 6 * d2 / (n * (n * n - 1))

insts = list(m)
scores = {name: {i: f(m[i]) for i in insts} for name, f in variants.items()}

uni = [i for i in insts if breadth[i] >= 0.75]
print("Universal-membership bodies (breadth >= 0.75), ranked by each variant:")
for name in variants:
    order = sorted(uni, key=lambda i: -scores[name][i])
    print(f"  {name:18s}: " + "  ".join(f"{i}({scores[name][i]:+.2f})" for i in order))

print("\nWAICO & China 2023 are the top two universal bodies (above UN & UNESCO)?")
for name in variants:
    order = sorted(uni, key=lambda i: -scores[name][i])
    top2 = set(order[:2]) == {"waico", "china_init"}
    print(f"  {name:18s}: {'YES' if top2 else 'NO '}  (order: {', '.join(order)})")

print("\nSpearman rank correlation across all 15 instruments vs the paper index:")
for name in ["V1 drop open", "V2 open penalised"]:
    print(f"  V0 vs {name:18s}: rho = {spearman(scores['V0 paper'], scores[name]):.3f}")
