"""Replace the principle-emphasis columns in institutions.csv with the 4-coder
full-document consensus (mean), and recompute norm_orientation. Structural columns
(membership breadth, formalization, legal force) are factual and left unchanged."""
import csv, json

PRIN = ["safety", "rights", "sovereignty", "development", "openness", "standards", "sustainability"]
COL = {"safety":"p_safety","rights":"p_rights","sovereignty":"p_sovereignty","development":"p_development",
       "openness":"p_open","standards":"p_standards","sustainability":"p_sustainability"}

cons = json.load(open("consensus_coding.json"))

def num(x):
    x = round(float(x), 3)
    return ("%g" % x)  # 0.625, 1, 0, -1.625 ...

rows = list(csv.DictReader(open("data/institutions.csv", encoding="utf-8")))
fields = rows[0].keys()
for r in rows:
    c = cons[r["inst_id"]]
    for p in PRIN:
        r[COL[p]] = num(c["means"][p])
    r["norm_orientation"] = num(c["orient"])

with open("data/institutions.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(fields))
    w.writeheader(); w.writerows(rows)

for r in sorted(rows, key=lambda r: -float(r["norm_orientation"])):
    print(f'{r["inst_id"]:14s} orient={r["norm_orientation"]:>6s} breadth={r["breadth"]}')
print("updated data/institutions.csv from 4-coder consensus")
