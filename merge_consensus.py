"""Merge Claude's full-document coding as a 4th coder, compute the 4-coder consensus
(the new document-grounded primary coding) and interval Krippendorff's alpha."""
import json, itertools

PRIN = ["safety", "rights", "sovereignty", "development", "openness", "standards", "sustainability"]

claude = {
 "waico":       {"safety":1,"rights":0.5,"sovereignty":0.5,"development":1,"openness":1,"standards":1,"sustainability":1},
 "china_init":  {"safety":1,"rights":1,"sovereignty":1,"development":1,"openness":0.5,"standards":0.5,"sustainability":0.5},
 "gpai":        {"safety":0,"rights":1,"sovereignty":0,"development":0.5,"openness":0,"standards":0,"sustainability":0},
 "oecd_ai":     {"safety":1,"rights":1,"sovereignty":0,"development":1,"openness":1,"standards":1,"sustainability":1},
 "eu_aiact":    {"safety":1,"rights":1,"sovereignty":0.5,"development":0.5,"openness":0,"standards":1,"sustainability":0.5},
 "coe_fcai":    {"safety":0.5,"rights":1,"sovereignty":0.5,"development":0,"openness":0,"standards":0,"sustainability":0},
 "g7_hiroshima":{"safety":1,"rights":1,"sovereignty":0.5,"development":0.5,"openness":0.5,"standards":1,"sustainability":0.5},
 "bletchley":   {"safety":1,"rights":1,"sovereignty":0.5,"development":1,"openness":0.5,"standards":0,"sustainability":0.5},
 "seoul":       {"safety":1,"rights":1,"sovereignty":0.5,"development":1,"openness":0,"standards":1,"sustainability":0.5},
 "aisi_net":    {"safety":1,"rights":0.5,"sovereignty":0,"development":0.5,"openness":0,"standards":0.5,"sustainability":0},
 "un_dialogue": {"safety":0.5,"rights":0.5,"sovereignty":0,"development":1,"openness":0.5,"standards":0.5,"sustainability":0.5},
 "unesco_rec":  {"safety":0.5,"rights":1,"sovereignty":0.5,"development":0.5,"openness":0.5,"standards":0.5,"sustainability":1},
 "au_strategy": {"safety":1,"rights":1,"sovereignty":0.5,"development":1,"openness":0.5,"standards":0.5,"sustainability":0.5},
 "asean_guide": {"safety":1,"rights":1,"sovereignty":0.5,"development":0.5,"openness":0,"standards":0.5,"sustainability":0.5},
 "brics_ai":    {"safety":1,"rights":1,"sovereignty":1,"development":1,"openness":1,"standards":1,"sustainability":1},
}

raw = json.load(open("reliability_fulltext_raw.json"))
raw["anthropic/claude-opus-4.8"] = {i: {p: float(v[p]) for p in PRIN} for i, v in claude.items()}
json.dump(raw, open("reliability_fulltext_raw.json", "w"), indent=1)

coders = list(raw.keys())
insts = list(raw[coders[0]].keys())
print("Coders (all full-document):", [c.split('/')[-1] for c in coders])

def orient(s):  # (sovereignty + development + openness) - (rights + safety)
    return (s["sovereignty"] + s["development"] + s["openness"]) - (s["rights"] + s["safety"])

def kalpha(units):
    Do = 0.0; n_total = 0
    for u in units:
        vals = [v for v in u if v is not None]
        m = len(vals)
        if m < 2: continue
        pair = sum((vals[a]-vals[b])**2 for a in range(m) for b in range(m) if a != b)
        Do += pair/(m-1); n_total += m
    Do /= n_total
    allv = [v for u in units for v in u if v is not None]
    De = sum((a-b)**2 for a in allv for b in allv)/(len(allv)*(len(allv)-1))
    return 1 - Do/De if De else 1.0

# alpha across the 4 full-document coders (all 7 principles x 15 instruments)
units = [[raw[c][i][p] for c in coders] for i in insts for p in PRIN]
print(f"\nInterval Krippendorff alpha, 4 full-document coders: {kalpha(units):.3f}")

# per-family alpha
print("Per-family alpha:")
for p in PRIN:
    u = [[raw[c][i][p] for c in coders] for i in insts]
    print(f"  {p:14s} {kalpha(u):.2f}")

# exact 4-way agreement
exact = sum(1 for i in insts for p in PRIN if len({raw[c][i][p] for c in coders}) == 1)
print(f"Exact 4-way agreement: {exact/(len(insts)*len(PRIN))*100:.0f}%")

# 4-coder consensus: mean principle scores and mean orientation, with range
print("\nConsensus (mean of 4 full-document coders):")
print(f"{'inst':14s} {'orient_mean':>11s} {'range':>12s}  consensus principle means (saf,rig,sov,dev,opn,std,sus)")
consensus = {}
rows = []
for i in insts:
    means = {p: sum(raw[c][i][p] for c in coders)/len(coders) for p in PRIN}
    os_ = [orient(raw[c][i]) for c in coders]
    om = sum(os_)/len(os_)
    consensus[i] = {"means": means, "orient": om, "lo": min(os_), "hi": max(os_)}
    rows.append((i, om, min(os_), max(os_), means))
for i, om, lo, hi, means in sorted(rows, key=lambda r: -r[1]):
    pm = ",".join(f"{means[p]:.2f}" for p in PRIN)
    print(f"{i:14s} {om:>11.2f} {('['+format(lo,'.1f')+','+format(hi,'.1f')+']'):>12s}  {pm}")

json.dump(consensus, open("consensus_coding.json", "w"), indent=1)
print("\nwrote consensus_coding.json")
