"""
WAICO paper - analysis of the coded institution dataset.
Reads data/institutions.csv, computes the membership-logic / normative-orientation
positions, the empty-cell finding, and a representation-gap summary, and renders
two figures. All quantities derive transparently from the coded variables.
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(HERE, "data", "institutions.csv"))

os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)

# ----- short labels for plotting -----
labels = {
    "waico": "WAICO", "china_init": "China GAIGI '23", "gpai": "GPAI",
    "oecd_ai": "OECD AI", "eu_aiact": "EU AI Act", "coe_fcai": "CoE Conv.",
    "g7_hiroshima": "G7 Hiroshima", "bletchley": "Bletchley", "seoul": "Seoul",
    "aisi_net": "AISI Network", "un_dialogue": "UN Dialogue", "unesco_rec": "UNESCO",
    "au_strategy": "AU Strategy", "asean_guide": "ASEAN", "brics_ai": "BRICS AI",
}
df["lab"] = df["inst_id"].map(labels)

# ----- bloc tag (for interpretation only) -----
def bloc(a):
    if a in ("China", "BRICS"): return "China / BRICS"
    if a in ("African Union", "ASEAN"): return "Global South regional"
    if a in ("UN", "UNESCO"): return "UN multilateral"
    return "West / like-minded"
df["bloc"] = df["lead_actor"].map(bloc)

# =====================================================================
# RESULT 1: the normative-orientation x membership-breadth map
#   x = norm_orientation  (negative = rights-safety pole, positive = sovereignty-development pole)
#   y = breadth           (0 = club, 1 = universal)
# =====================================================================
# Region of interest: universal (breadth >= 0.75) AND on the sovereignty-development
# side of the axis (norm_orientation > 0, the natural midpoint between the poles)
mask_cell = (df["breadth"] >= 0.75) & (df["norm_orientation"] > 0.0)
print("== RESULT 1: universal + development-leaning region (orientation > 0) ==")
print(df.loc[mask_cell, ["lab", "norm_orientation", "breadth"]].sort_values("norm_orientation", ascending=False).to_string(index=False))
print()
print("== universal-membership bodies ranked by orientation ==")
print(df[df["breadth"] >= 0.75].sort_values("norm_orientation", ascending=False)[["lab", "norm_orientation", "breadth"]].to_string(index=False))
print()

# WAICO nearest neighbour in the 2D space
coords = df[["norm_orientation", "breadth"]].to_numpy(dtype=float)
i_waico = df.index[df["inst_id"] == "waico"][0]
d = np.sqrt(((coords - coords[i_waico]) ** 2).sum(axis=1))
order = np.argsort(d)
print("WAICO nearest neighbours (2D euclidean):")
for j in order[1:4]:
    print(f"  {df.iloc[j]['lab']:16s} dist={d[j]:.2f}")
print()

# mean normative orientation: values-gated entry vs values-neutral entry
vg = df[df["accession_normative_test"] == 1]["norm_orientation"]
vn = df[df["accession_normative_test"] == 0]["norm_orientation"]
print(f"mean norm_orientation, values-gated entry (n={len(vg)}): {vg.mean():+.2f}")
print(f"mean norm_orientation, values-neutral entry (n={len(vn)}): {vn.mean():+.2f}")
print()

# =====================================================================
# RESULT 3: representation / development-orientation gap
# =====================================================================
west = df[df["bloc"] == "West / like-minded"]
rest = df[df["bloc"] != "West / like-minded"]
print("== RESULT 3: development orientation by bloc ==")
print(df.groupby("bloc")[["development_orientation", "global_south_priority"]].mean().round(2).to_string())
print()
print(f"share global_south_priority=1, West/like-minded (n={len(west)}): {west['global_south_priority'].mean():.2f}")
print(f"share global_south_priority=1, all others       (n={len(rest)}): {rest['global_south_priority'].mean():.2f}")
print()

# =====================================================================
# RESULT 2: institutional definedness
# =====================================================================
print("== RESULT 2: definedness score (0-5) ==")
print(df.sort_values("definedness")[["lab", "status", "definedness"]].to_string(index=False))
print()

# ---------------------------------------------------------------------
# FIGURE 1 : the map
# ---------------------------------------------------------------------
bloc_marker = {
    "China / BRICS": ("o", "#c0392b"),
    "Global South regional": ("^", "#e67e22"),
    "UN multilateral": ("s", "#7f8c8d"),
    "West / like-minded": ("D", "#2c3e50"),
}
fig, ax = plt.subplots(figsize=(8.4, 6.4))
for b, (mk, col) in bloc_marker.items():
    sub = df[df["bloc"] == b]
    ax.scatter(sub["norm_orientation"], sub["breadth"], s=55 + sub["development_orientation"] * 80,
               marker=mk, facecolor=col, edgecolor="black", linewidth=0.6, alpha=0.85, label=b, zorder=3)

# Per-coder orientation ranges are reported in the reliability section and in
# consensus_coding.json; they are not drawn on the map because several bodies share the
# same membership breadth, which would stack their horizontal ranges on one line.

# per-institution label offsets (dx pt, dy pt, horizontal alignment) to limit overlap
offsets = {
    "waico": (6, 5, "left"), "china_init": (0, -14, "center"),
    "gpai": (6, 5, "left"), "oecd_ai": (7, 4, "left"),
    "eu_aiact": (6, 5, "left"), "coe_fcai": (-7, 6, "right"),
    "g7_hiroshima": (6, -12, "left"), "bletchley": (6, 5, "left"),
    "seoul": (6, -13, "left"), "aisi_net": (6, -12, "left"),
    "un_dialogue": (0, -14, "center"), "unesco_rec": (-8, 4, "right"),
    "au_strategy": (6, 5, "left"), "asean_guide": (6, -12, "left"),
    "brics_ai": (6, 5, "left"),
}
for _, r in df.iterrows():
    dx, dy, ha = offsets.get(r["inst_id"], (6, 5, "left"))
    ax.annotate(r["lab"], (r["norm_orientation"], r["breadth"]),
                xytext=(dx, dy), textcoords="offset points", fontsize=8.2, ha=ha, zorder=4)

# guide lines and the highlighted region (universal + development-leaning)
ax.axvline(0, color="grey", lw=0.7, ls="--", zorder=1)
ax.axhline(0.75, color="grey", lw=0.7, ls=":", zorder=1)
ax.add_patch(plt.Rectangle((0.25, 0.75), 0.95, 0.32, facecolor="#f1c40f", alpha=0.18, zorder=0))
ax.text(0.725, 0.80, "universal +\ndevelopment-leaning", fontsize=8.0, ha="center", va="center", color="#7f6000")

ax.set_xlabel("Normative orientation     (left: rights and safety     right: sovereignty, development, openness)", fontsize=9.2)
ax.set_ylabel("Membership breadth     (0 = club     1 = universal)", fontsize=9.5)
ax.set_title("Figure 1. The global AI governance landscape and WAICO's position", fontsize=11)
ax.set_xlim(-2.4, 1.7)
ax.set_ylim(0.15, 1.08)
ax.set_xticks([-2, -1, 0, 1])
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.grid(True, alpha=0.18)

# two legends: lead bloc (colors/markers) and development orientation (marker size)
# fixed, uniform marker handles so the legend symbols do not inherit the variable
# data-point sizes (which made them overlap)
bloc_handles = [Line2D([0], [0], marker=mk, linestyle="none", markerfacecolor=col,
                       markeredgecolor="black", markeredgewidth=0.6, markersize=8.5, label=b)
                for b, (mk, col) in bloc_marker.items()]
leg1 = ax.legend(handles=bloc_handles, loc="upper left", bbox_to_anchor=(0.005, 0.72),
                 fontsize=8.2, framealpha=0.9, title="Lead bloc", title_fontsize=8.4,
                 labelspacing=0.9, handletextpad=0.6, borderpad=0.7)
ax.add_artist(leg1)
size_handles = [ax.scatter([], [], s=55 + dv * 80, marker="o", facecolor="0.75",
                           edgecolor="black", linewidth=0.5) for dv in (0, 1, 2)]
ax.legend(size_handles, ["low (0)", "medium (1)", "high (2)"], loc="lower right",
          fontsize=7.8, title="Development\norientation", title_fontsize=8.0,
          framealpha=0.9, labelspacing=1.0, borderpad=0.7)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "figures", "fig1_map.png"), dpi=200)
fig.savefig(os.path.join(HERE, "figures", "fig1_map.pdf"))
print("wrote figures/fig1_map.png/.pdf")

# ---------------------------------------------------------------------
# FIGURE 2 : institutional definedness
# ---------------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(8.0, 5.0))
ds = df.sort_values("definedness")
colors = ["#c0392b" if s == "proposed" else "#2c3e50" for s in ds["status"]]
ax2.barh(ds["lab"], ds["definedness"], color=colors, edgecolor="black", linewidth=0.5)
ax2.set_xlabel("Formalization score (0-5: charter, secretariat, budget, voting rules, defined membership)")
ax2.set_title("Figure 2. Institutional formalization across the regime complex\n(red = proposed; for binding legal instruments the score reflects their implementing apparatus)")
ax2.set_xlim(0, 5.2)
for i, (v, s) in enumerate(zip(ds["definedness"], ds["status"])):
    ax2.text(v + 0.08, i, f"{v:.0f}", va="center", fontsize=8)
fig2.tight_layout()
fig2.savefig(os.path.join(HERE, "figures", "fig2_definedness.png"), dpi=200)
fig2.savefig(os.path.join(HERE, "figures", "fig2_definedness.pdf"))
print("wrote figures/fig2_definedness.png/.pdf")
