import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from collections import Counter
from pathlib import Path

base_path = Path("/Users/kqqs967/Library/CloudStorage/OneDrive-AZCollaboration/CORE/PhD/KC_KSA")

# ── Keyword normalisation: collapse near-duplicates to one canonical form ─────
# Terms to drop entirely (Scopus metadata tags, not clinical content)
DROP_TERMS = {
    'adult', 'article', 'female', 'male', 'human', 'humans', 'aged',
    'middle aged', 'young adult', 'adolescent', 'child', 'children',
    'priority journal', 'controlled study', 'major clinical study',
    'prospective study', 'retrospective study', 'observational study',
    'cross-sectional study', 'cohort study', 'follow up', 'follow-up',
    'clinical article', 'journal article', 'comparative study',
    'unclassified drug', 'drug dose', 'outcome assessment',
    'saudi arabia', 'saudi', 'arabia', 'case report',
    'retrospective studies', 'procedures',
}

NORMALISE = {
    "cornea transplantation":                   "corneal transplantation",
    "corneal transplant":                    "corneal transplantation",
    "corneal transplants":                   "corneal transplantation",
    "keratoplasty":                          "corneal transplantation",
    "pkp":                                   "penetrating keratoplasty",
    "pk":                                    "penetrating keratoplasty",
    "keratoplasty, penetrating":             "penetrating keratoplasty",
    "penetrating keratoplasty (pk)":         "penetrating keratoplasty",
    "dalk":                                  "deep anterior lamellar keratoplasty",
    "alk":                                   "deep anterior lamellar keratoplasty",
    "deep anterior lamellar keratoplasty (dalk)": "deep anterior lamellar keratoplasty",
    "femtosecond":                           "femtosecond laser",
    "ccl":                                   "corneal collagen cross-linking",
    "cxl":                                   "corneal collagen cross-linking",
    "corneal cross-linking":                 "corneal collagen cross-linking",
    "collagen cross-linking":                "corneal collagen cross-linking",
    "icrs":                                  "intrastromal corneal ring segments",
    "intacs":                                "intrastromal corneal ring segments",
    "scheimpflug camera":                    "pentacam",
    "scheimpflug":                           "pentacam",
    "corneal topography":                    "corneal topography / tomography",
    "corneal tomography":                    "corneal topography / tomography",
}

def parse_keywords(s):
    if pd.isna(s):
        return []
    tokens = []
    for k in s.split(";"):
        k = re.sub(r"\s+", " ", k.strip().lower())
        if k:
            k = NORMALISE.get(k, k)
            if k not in DROP_TERMS:
                tokens.append(k)
    return tokens

df = pd.read_csv(base_path / "KC_KSA_kc_specific_enriched.csv")

early_df = df[df["year"].between(2000, 2012)]
late_df  = df[df["year"].between(2013, 2024)]

early_kw = Counter(k for s in early_df["all_keywords"].dropna() for k in parse_keywords(s))
late_kw  = Counter(k for s in late_df["all_keywords"].dropna()  for k in parse_keywords(s))

# Adaptive top-N: cap early at however many unique keywords exist (max 10)
N_EARLY = min(10, len(early_kw))
N_LATE  = 20

top_early = early_kw.most_common(N_EARLY)
top_late  = late_kw.most_common(N_LATE)

early_set = {k for k, _ in top_early}
late_set  = {k for k, _ in top_late}
shared    = early_set & late_set

print(f"Early period keywords with data: {len(early_kw)} unique, showing top {N_EARLY}")
print(f"Late  period keywords with data: {len(late_kw)} unique, showing top {N_LATE}")
print(f"Shared (bold): {sorted(shared)}")

# ── Plot ──────────────────────────────────────────────────────────────────────
TEAL   = "#2A9D8F"
CORAL  = "#E76F51"

fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(16, 9), dpi=300)
fig.suptitle("Evolution of Research Themes in Keratoconus Publications\nfrom Saudi Arabia",
             fontsize=14, fontweight="bold", y=0.98)

def draw_panel(ax, top_kw, shared_kw, color, title, coverage_note):
    labels  = [k for k, _ in top_kw]
    counts  = [n for _, n in top_kw]
    y_pos   = range(len(labels))

    bars = ax.barh(list(y_pos), counts, color=color, edgecolor="white",
                   linewidth=0.6, height=0.7)

    # Count labels
    for bar, n in zip(bars, counts):
        ax.text(n + 0.05, bar.get_y() + bar.get_height() / 2,
                str(n), va="center", fontsize=9, fontweight="bold")

    # Y-tick labels — bold if shared
    ax.set_yticks(list(y_pos))
    tick_labels = []
    for lbl in labels:
        weight = "bold" if lbl in shared_kw else "normal"
        tick_labels.append(lbl.title())   # title-case for display
        # matplotlib doesn't support per-tick bold via set_yticklabels directly,
        # so we draw them manually and hide the default ticks
    ax.set_yticklabels([""] * len(labels))   # blank out defaults

    for i, lbl in enumerate(labels):
        weight = "bold" if lbl in shared_kw else "normal"
        ax.text(-0.02, i, lbl.title(), ha="right", va="center",
                fontsize=9, fontweight=weight, transform=ax.get_yaxis_transform())

    ax.set_xlim(0, max(counts) + 1.5)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.set_xlabel("Keyword frequency", fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=10, color=color)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", alpha=0.3)
    ax.set_axisbelow(True)
    ax.invert_yaxis()   # highest count at top

    # Coverage note
    ax.text(0.98, 0.01, coverage_note, transform=ax.transAxes,
            fontsize=8, color="#666666", ha="right", va="bottom", style="italic")

early_note = f"{early_df['all_keywords'].notna().sum()}/{len(early_df)} papers have keywords"
late_note  = f"{late_df['all_keywords'].notna().sum()}/{len(late_df)} papers have keywords"

draw_panel(ax_l, top_early, shared,
           TEAL,  "2000 – 2012  (Early Period)", early_note)
draw_panel(ax_r, top_late,  shared,
           CORAL, "2013 – 2024  (Recent Period)", late_note)

# Shared-theme legend
from matplotlib.lines import Line2D
legend_el = [Line2D([0], [0], color="none", label="Bold = keyword appears in both periods")]
fig.legend(handles=legend_el, loc="lower center", fontsize=9,
           frameon=True, framealpha=0.85, bbox_to_anchor=(0.5, 0.005))

plt.tight_layout(rect=[0, 0.03, 1, 0.96])

out = base_path / "fig6_thematic_evolution.png"
plt.savefig(out, dpi=300, bbox_inches="tight", format="png")
print(f"\n✓ Saved: {out}")
plt.close()
