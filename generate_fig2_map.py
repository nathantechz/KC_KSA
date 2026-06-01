import re
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
from pathlib import Path
from collections import Counter

base_path = Path("/Users/kqqs967/Library/CloudStorage/OneDrive-AZCollaboration/CORE/PhD/KC_KSA")
SHAPEFILE = "/tmp/ne_110m_countries/ne_110m_admin_0_countries.shp"

# ── Name reconciliation: affiliation string → NAME_LONG in shapefile ──────────
NAME_MAP = {
    "United States":          "United States",
    "United Kingdom":         "United Kingdom",
    "Saudi Arabia":           "Saudi Arabia",
    "Italy":                  "Italy",
    "Egypt":                  "Egypt",
    "Singapore":              "Singapore",
    "Switzerland":            "Switzerland",
    "Jordan":                 "Jordan",
    "India":                  "India",
    "Ireland":                "Ireland",
    "Canada":                 "Canada",
    "Pakistan":               "Pakistan",
    "Bahrain":                "Bahrain",
    "Brazil":                 "Brazil",
    "Spain":                  "Spain",
    "Malaysia":               "Malaysia",
    "Morocco":                "Morocco",
    "Sudan":                  "Sudan",
    "China":                  "China",
    "Poland":                 "Poland",
    "United Arab Emirates":   "United Arab Emirates",
    "Qatar":                  "Qatar",
    "Austria":                "Austria",
    "Australia":              "Australia",
    "Colombia":               "Colombia",
}

# ── Extract country from last comma-token of each affiliation segment ─────────
def extract_country(aff_segment):
    parts = [p.strip() for p in aff_segment.split(",")]
    last = re.sub(r'^[\d\s]+', '', parts[-1]).strip()
    # strip HTML entities (e.g. "& amp")
    last = re.sub(r'&\s*\w+', '', last).strip()
    return NAME_MAP.get(last)

df = pd.read_csv(base_path / "KC_KSA_kc_specific.csv")

# Per paper: collect unique countries, then count Saudi co-authorship pairs
collab_counter = Counter()
for raw in df["affiliations"].dropna():
    countries = set()
    for seg in raw.split(";"):
        c = extract_country(seg.strip())
        if c:
            countries.add(c)
    if "Saudi Arabia" in countries:
        for c in countries:
            if c != "Saudi Arabia":
                collab_counter[c] += 1

print("Collaboration counts (papers co-authored with Saudi Arabia):")
for country, n in sorted(collab_counter.items(), key=lambda x: -x[1]):
    print(f"  {n:3d}  {country}")

# ── Load shapefile and merge counts ──────────────────────────────────────────
world = gpd.read_file(SHAPEFILE)
world = world[["NAME_LONG", "geometry"]].copy()
world["collab"] = world["NAME_LONG"].map(collab_counter).fillna(0)

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(18, 10), dpi=300)

# Base layer: all countries in light grey
world[world["NAME_LONG"] != "Saudi Arabia"].plot(
    ax=ax, color="#e8e8e8", edgecolor="#aaaaaa", linewidth=0.3
)

# Collaborating countries: blue sequential colormap (exclude Saudi Arabia)
collabs = world[(world["collab"] > 0) & (world["NAME_LONG"] != "Saudi Arabia")]
non_collabs = world[(world["collab"] == 0) & (world["NAME_LONG"] != "Saudi Arabia")]

# Re-plot non-collaborating on top of base (already done above, just for clarity)
vmax = collab_counter.most_common(1)[0][1]   # actual data max, not shapefile max
cmap = plt.cm.Blues
norm = mcolors.Normalize(vmin=0.5, vmax=vmax)

collabs.plot(
    ax=ax, column="collab", cmap=cmap, norm=norm,
    edgecolor="#555555", linewidth=0.4
)

# Saudi Arabia in gold
world[world["NAME_LONG"] == "Saudi Arabia"].plot(
    ax=ax, color="#FFD700", edgecolor="#333333", linewidth=0.8
)

# ── Colorbar ─────────────────────────────────────────────────────────────────
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, orientation="vertical",
                    fraction=0.018, pad=0.02, shrink=0.6)
cbar.set_label("Co-authored papers with Saudi Arabia", fontsize=10)
cbar.ax.tick_params(labelsize=9)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_elements = [
    Patch(facecolor="#FFD700", edgecolor="#333333", label="Saudi Arabia (focal country)"),
    Patch(facecolor=cmap(norm(1)),  edgecolor="#555555", label="1 co-authored paper"),
    Patch(facecolor=cmap(norm(max(1, vmax // 2))), edgecolor="#555555",
          label=f"~{int(vmax // 2)} co-authored papers"),
    Patch(facecolor=cmap(norm(vmax)), edgecolor="#555555", label=f"{int(vmax)} co-authored papers"),
    Patch(facecolor="#e8e8e8", edgecolor="#aaaaaa", label="No collaboration"),
]
ax.legend(handles=legend_elements, loc="lower left", fontsize=9, framealpha=0.9)

# ── Labels for top collaborators ─────────────────────────────────────────────
LABEL_COORDS = {
    "United Kingdom":  (-2,   54),
    "United States":   (-100, 40),
    "Italy":           (20,   41),   # shifted right to avoid Switzerland overlap
    "Egypt":           (30,   27),
    "Singapore":       (104,   1),
    "Switzerland":     (8,    47),
    "Jordan":          (37,   31),
    "Australia":       (134, -25),   # n=1, confirmed in data
}
for country, (lx, ly) in LABEL_COORDS.items():
    n = collab_counter.get(country, 0)
    if n > 0:
        ax.annotate(f"{country}\n(n={n})", xy=(lx, ly), fontsize=7.5,
                    ha="center", color="#222222",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                              alpha=0.7, edgecolor="none"))

ax.set_title(
    "International Research Collaborations on Keratoconus in Saudi Arabia",
    fontsize=14, fontweight="bold", pad=14
)
ax.set_axis_off()

fig.text(0.01, 0.01,
         "Each unit = one paper with ≥1 Saudi and ≥1 non-Saudi affiliation. "
         "Source: KC_KSA_kc_specific.csv (n=118 papers).",
         fontsize=8, color="#555555", style="italic")

plt.tight_layout(rect=[0, 0.03, 1, 1])

out = base_path / "fig2_country_collaboration_v2.png"
plt.savefig(out, dpi=300, bbox_inches="tight", format="png")
print(f"\n✓ Saved: {out}")
plt.close()
