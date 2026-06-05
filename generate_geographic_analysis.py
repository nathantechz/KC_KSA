import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter
from difflib import SequenceMatcher

# Load KC-specific dataset
base_path = Path("/Users/kqqs967/Library/CloudStorage/OneDrive-AZCollaboration/CORE/PhD/KC_KSA")
kc_specific_file = base_path / "KC_KSA_kc_specific.csv"

print("Loading KC_KSA_kc_specific.csv...")
df = pd.read_csv(kc_specific_file)
df = df[(df['year'] >= 2000) & (df['year'] <= 2025)].copy()
assert len(df) == 99, f"Expected 99 rows, got {len(df)}"

print(f"Total KC-specific records (2000-2025): {len(df)}")

# Extract institutions from affiliations
def extract_institutions(affiliation_str):
    """Extract institution names from affiliations field"""
    if pd.isna(affiliation_str) or affiliation_str == '':
        return []
    # Split by semicolon for multiple affiliations
    institutions = [inst.strip() for inst in str(affiliation_str).split(';')]
    return [inst for inst in institutions if inst]

# Canonical institution names and the substrings that map to them.
# Order matters: more specific patterns should come first.
CANONICAL_INSTITUTIONS = [
    ("King Khaled Eye Specialist Hospital",
     ["king khaled eye specialist", "king khalid eye specialist", "kkesh"]),
    ("King Saud University",
     ["king saud university", "king saud univ", " ksu"]),
    ("King Saud Medical City",
     ["king saud medical city"]),
    ("King Abdulaziz University",
     ["king abdulaziz university", "king abdulaziz univ", " kau"]),
    ("King Abdulaziz University Hospital",
     ["king abdulaziz university hospital"]),
    ("King Abdulaziz Specialist Hospital Al Jouf",
     ["king abdulaziz specialist hospital"]),
    ("King Saud Bin Abdulaziz University for Health Sciences (Riyadh)",
     ["king saud bin abdulaziz university for health sciences, riyadh",
      "king saud bin abdulaziz university for health sciences (ksau-hs), riyadh",
      "ksau-hs), riyadh"]),
    ("King Saud Bin Abdulaziz University for Health Sciences (Jeddah)",
     ["king saud bin abdulaziz"]),
    ("King Abdullah International Medical Research Center",
     ["king abdullah international medical research"]),
    ("King Fahad Armed Forces Hospital",
     ["king fahad armed forces"]),
    ("King Khalid University Abha",
     ["king khalid university"]),
    ("Dhahran Eye Specialist Hospital",
     ["dhahran eye"]),
    ("Magrabi Eye Hospital",
     ["magrabi"]),
    ("University of Ferrara",
     ["university of ferrara", "università di ferrara"]),
    ("Ospedali Privati Forlì Villa Igea",
     ["ospedali privati forl", "villa igea"]),
    ("IRFO Forlì",
     ["istituto internazionale per la ricerca", "irfo"]),
    ("University of Hafr Al Batin",
     ["university of hafr al batin", "hafr al batin"]),
    ("Newcastle University",
     ["newcastle university", "newcastle upon tyne"]),
    ("National Guard Hospital Medina",
     ["national guard hospital, medina", "national guard hospital, al-madinah"]),
    ("Taibah University",
     ["taibah university"]),
    ("Ministry of Health",
     ["ministry of health"]),
]

def normalize_institution(inst_name):
    """Map any variant of an institution name to its canonical form."""
    inst_lower = inst_name.lower()
    for canonical, patterns in CANONICAL_INSTITUTIONS:
        if any(p in inst_lower for p in patterns):
            return canonical
    return inst_name.strip()

def fuzzy_merge_counts(counts, max_edit_distance=5):
    """Merge remaining duplicate keys whose edit distance is within threshold."""
    keys = list(counts.keys())
    merged = {}
    absorbed = set()
    for i, k1 in enumerate(keys):
        if k1 in absorbed:
            continue
        total = counts[k1]
        for k2 in keys[i + 1:]:
            if k2 in absorbed:
                continue
            # Use length-normalised edit distance on the shorter string
            longer = max(len(k1), len(k2))
            distance = int((1 - SequenceMatcher(None, k1.lower(), k2.lower()).ratio()) * longer)
            if distance <= max_edit_distance:
                total += counts[k2]
                absorbed.add(k2)
        merged[k1] = total
    return Counter(merged)

# Extract and normalize institutions
all_institutions = []
for affiliation_list in df['affiliations'].apply(extract_institutions):
    for inst in affiliation_list:
        normalized = normalize_institution(inst)
        all_institutions.append(normalized)

# Count institutions, then fuzzy-merge residual near-duplicates
institution_counts = fuzzy_merge_counts(Counter(all_institutions))
top_15_institutions = institution_counts.most_common(15)

print(f"\nTotal unique institutions: {len(institution_counts)}")
print(f"\nTop 15 institutions (before city assignment):")
for idx, (inst, count) in enumerate(top_15_institutions, 1):
    print(f"{idx:2d}. {count:3d} - {inst[:70]}")

SAUDI_KEYWORDS = [
    'saudi', 'riyadh', 'jeddah', 'dammam', 'khobar', 'dhahran',
    'madinah', 'makkah', 'najran', 'king saud', 'king khaled', 'king khalid',
    'king abdulaziz', 'king fahad', 'king faisal', 'king abdullah',
    'magrabi', 'kkesh', 'dhahran eye',
]

def get_city_for_institution(inst_name):
    inst_lower = inst_name.lower()
    # Riyadh
    if any(k in inst_lower for k in ['king khaled eye', 'king khalid eye', 'kkesh',
                                      'king saud university', 'king saud medical',
                                      'riyadh', 'national guard health affairs',
                                      'ksau-hs (riyadh)', '(riyadh)']):
        return 'Riyadh'
    # Jeddah
    if any(k in inst_lower for k in ['jeddah', 'king abdulaziz', 'magrabi',
                                      'king saud bin abdulaziz', 'king abdullah international',
                                      'umm al-qura', 'king fahad armed']):
        return 'Jeddah'
    # Dammam / Eastern Province
    if any(k in inst_lower for k in ['dammam', 'khobar', 'dhahran', 'eastern', 'najran']):
        return 'Dammam'
    # Other Saudi
    if any(k in inst_lower for k in SAUDI_KEYWORDS + [
        'taibah', 'hafr al batin', 'national guard hospital', 'ministry of health',
        'king khalid university', 'abha',
    ]):
        return 'Other Saudi'
    # International
    return 'International'

# Create dataframe for top 15
top15_df = pd.DataFrame(top_15_institutions, columns=['institution', 'count'])

# Assign cities using smart matching
top15_df['city'] = top15_df['institution'].apply(get_city_for_institution)

# Sort by count descending (ascending for horizontal bar chart display)
top15_df = top15_df.sort_values('count', ascending=True)

print(f"\n" + "="*80)
print("TOP 15 INSTITUTIONS - CITY ASSIGNMENT")
print("="*80)
print(top15_df[['institution', 'count', 'city']].to_string(index=False))

# Create horizontal bar chart
fig, ax = plt.subplots(figsize=(18, 11), dpi=300)

# Define colors by city (5 categories)
color_map = {
    'Riyadh':        '#2E86AB',  # Blue
    'Jeddah':        '#E84393',  # Pink
    'Dammam':        '#F18F01',  # Orange
    'Other Saudi':   '#3BB273',  # Green
    'International': '#999999',  # Gray
}

colors = [color_map.get(city, '#999999') for city in top15_df['city']]

# Create bars
bars = ax.barh(range(len(top15_df)), top15_df['count'], color=colors, edgecolor='black', linewidth=0.7)

# Add count labels — always inside for the longest bar, outside for all others
max_count = max(top15_df['count'])
for bar, count in zip(bars, top15_df['count']):
    cy = bar.get_y() + bar.get_height() / 2
    if count == max_count:
        ax.text(count / 2, cy, f'{int(count)}',
                va='center', ha='center', fontsize=11, fontweight='bold', color='white',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7, edgecolor='none'))
    else:
        ax.text(count + 0.3, cy, f'{int(count)}',
                va='center', fontsize=10, fontweight='bold')

# Threshold line at x=5 — label anchored just above x-axis (y=0.3) to avoid top clipping
ax.axvline(x=5, color='#333333', linestyle='--', linewidth=1.2, zorder=3)
ax.text(5.2, 0.3, '≥5 publications threshold',
        fontsize=9, color='#333333', va='bottom')

# Set x-axis limit with extra space
ax.set_xlim(0, max_count + 4)

import textwrap

# Build wrapped labels — wrap at 40 chars so longest lines stay within left margin
wrapped_labels = [textwrap.fill(inst, width=40) for inst in top15_df['institution']]

# Count max lines needed to set bar height spacing
max_lines = max(lbl.count('\n') + 1 for lbl in wrapped_labels)

# Increase figure height if multi-line labels are present
fig_height = max(10, 10 + max(0, max_lines - 1))
fig.set_size_inches(18, fig_height)

# Hide default y tick labels and draw manually with ha='right'
ax.set_yticks(range(len(top15_df)))
ax.set_yticklabels([""] * len(top15_df))
for i, lbl in enumerate(wrapped_labels):
    ax.text(-0.01, i, lbl, ha='right', va='center', fontsize=9,
            transform=ax.get_yaxis_transform())

ax.set_xlabel('Number of Publications', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Institutions Publishing on Keratoconus in Saudi Arabia', 
            fontsize=14, fontweight='bold', pad=20)

# Add grid
ax.grid(True, alpha=0.3, axis='x')
ax.set_axisbelow(True)

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=color_map['Riyadh'],        edgecolor='black', label='Riyadh'),
    Patch(facecolor=color_map['Jeddah'],        edgecolor='black', label='Jeddah'),
    Patch(facecolor=color_map['Dammam'],        edgecolor='black', label='Dammam'),
    Patch(facecolor=color_map['Other Saudi'],   edgecolor='black', label='Other Saudi'),
    Patch(facecolor=color_map['International'], edgecolor='black', label='International'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=11, framealpha=0.95)

# Add statistics box
stats_text = f'Total Institutions: {len(institution_counts)}\nTop 15 shown\nTotal papers (2000–2025): {len(df)}'
ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
       fontsize=10, verticalalignment='top', horizontalalignment='right',
       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Footnote below the axes
fig.text(0.01, 0.01,
         '* One non-ophthalmology department included (Pharmacy); '
         'present due to co-authorship on genetics studies.',
         fontsize=9, color='#444444', va='bottom', style='italic')

fig.subplots_adjust(left=0.30, right=0.97, top=0.93, bottom=0.08)

# Save figure
fig_file = base_path / "fig3_institutions_v3.png"
plt.savefig(fig_file, dpi=300, bbox_inches='tight', format='png')
print(f"\n✓ Figure saved to: {fig_file}")
print(f"  Resolution: 300 DPI")
print(f"  Format: PNG")

plt.close()

print("\n" + "="*80)
print("✓ ANALYSIS COMPLETE")
print("="*80)
