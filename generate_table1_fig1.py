import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from scipy.interpolate import UnivariateSpline
from pathlib import Path

# Load the clean master dataset
base_path = Path("/Users/kqqs967/Library/CloudStorage/OneDrive-AZCollaboration/CORE/PhD/KC_KSA")
master_file = base_path / "KC_KSA_clean_master.csv"

print("Loading KC_KSA_clean_master.csv...")
df = pd.read_csv(master_file)

# ============================================================================
# TABLE 1: DESCRIPTIVE SUMMARY STATISTICS
# ============================================================================
print("\n" + "="*80)
print("TABLE 1: DESCRIPTIVE SUMMARY STATISTICS FOR KERATOCONUS SAUDI ARABIA (KC_KSA)")
print("="*80)

# Basic counts
total_records = len(df)
year_min = int(df['year'].min())
year_max = int(df['year'].max())
year_range = f"{year_min} - {year_max}"

print(f"\nTotal Records: {total_records}")
print(f"Year Range: {year_range}")

# Records per source
print(f"\nRecords per Source:")
source_counts = df['source'].value_counts().to_dict()
for source, count in sorted(source_counts.items()):
    pct = (count / total_records) * 100
    print(f"  {source:10s}: {count:4d} ({pct:5.1f}%)")

# Unique journals
unique_journals = df['journal'].nunique()
print(f"\nUnique Journals: {unique_journals}")
top_journals = df['journal'].value_counts().head(5)
print("  Top 5 journals:")
for journal, count in top_journals.items():
    print(f"    - {journal}: {count} publications")

# Unique authors - count unique names
def split_authors(author_str):
    if pd.isna(author_str) or author_str == '':
        return []
    return [a.strip() for a in str(author_str).split(';') if a.strip()]

df['authors_list'] = df['authors'].apply(split_authors)
all_authors = []
for author_list in df['authors_list']:
    all_authors.extend(author_list)
unique_authors = len(set(all_authors))
print(f"\nUnique Authors: {unique_authors}")

# Unique institutions - extract from affiliations
def extract_institutions(affiliation_str):
    if pd.isna(affiliation_str) or affiliation_str == '':
        return []
    # Split by semicolon for multiple affiliations
    institutions = [inst.strip() for inst in str(affiliation_str).split(';')]
    return [inst for inst in institutions if inst]

df['institutions_list'] = df['affiliations'].apply(extract_institutions)
all_institutions = []
for inst_list in df['institutions_list']:
    all_institutions.extend(inst_list)
unique_institutions = len(set(all_institutions))
print(f"\nUnique Institutions: {unique_institutions}")
print("  Top 10 institutions:")
from collections import Counter
institution_counts = Counter(all_institutions).most_common(10)
for inst, count in institution_counts:
    if len(inst) > 70:
        inst = inst[:67] + "..."
    print(f"    {count:2d} - {inst}")

# Missing affiliations
missing_aff = df['affiliation_missing'].sum()
print(f"\nRecords with Missing Affiliations: {missing_aff} ({(missing_aff/total_records)*100:.1f}%)")

# Citation statistics
print(f"\nCitation Statistics:")
print(f"  Mean citations: {df['citations'].mean():.1f}")
print(f"  Median citations: {df['citations'].median():.0f}")
print(f"  Max citations: {int(df['citations'].max())}")
print(f"  Min citations: {int(df['citations'].min())}")

# Create summary table for export
summary_table = pd.DataFrame({
    'Metric': [
        'Total Records',
        'Year Range',
        'Pubmed Records',
        'Scopus Records',
        'Unique Journals',
        'Unique Authors',
        'Unique Institutions',
        'Missing Affiliations',
        'Mean Citations',
        'Median Citations'
    ],
    'Value': [
        str(total_records),
        year_range,
        str(source_counts.get('PubMed', 0)),
        str(source_counts.get('Scopus', 0)),
        str(unique_journals),
        str(unique_authors),
        str(unique_institutions),
        f"{missing_aff} ({(missing_aff/total_records)*100:.1f}%)",
        f"{df['citations'].mean():.1f}",
        f"{df['citations'].median():.0f}"
    ]
})

summary_file = base_path / "KC_KSA_Table1_Summary.csv"
summary_table.to_csv(summary_file, index=False)
print(f"\n✓ Summary table saved to: {summary_file}")

# ============================================================================
# FIGURE 1: ANNUAL PUBLICATION TREND WITH LINEAR REGRESSION
# ============================================================================
print("\n" + "="*80)
print("FIGURE 1: ANNUAL PUBLICATION TREND")
print("="*80)

# Filter to analysis period: 2000-2025 (exclude pre-2000 sparse years and partial 2026)
df = df[df['year'].between(2000, 2025)].copy()
total_records = len(df)

# Count publications per year
pub_per_year = df.groupby('year').size().reset_index(name='count')
pub_per_year = pub_per_year.sort_values('year')

print(f"\nPublications per year (first 10 years):")
print(pub_per_year.head(10).to_string(index=False))

# Create figure with high DPI for publication
fig, ax = plt.subplots(figsize=(14, 8), dpi=300)

# Separate 2025 (most recent complete year) — no partial-year hatching needed
complete_years = pub_per_year.copy()

# Plot bars for all years 2000-2025
bars_complete = ax.bar(complete_years['year'], complete_years['count'],
                        color='#2E86AB', alpha=0.8, width=0.8, edgecolor='black', linewidth=0.5,
                        label='Complete year')

# LOESS smoothing for years >= 2000 and <= 2025 (excludes sparse 1990s and partial 2026)
loess_data = pub_per_year[(pub_per_year['year'] >= 2000) & (pub_per_year['year'] <= 2025)].copy()

if len(loess_data) > 3:
    from scipy.signal import savgol_filter
    window_length = min(11, len(loess_data) if len(loess_data) % 2 == 1 else len(loess_data) - 1)
    if window_length >= 5:
        smoothed = savgol_filter(loess_data['count'], window_length=window_length, polyorder=3)
        ax.plot(loess_data['year'], smoothed, color='#A23B72', linewidth=2.8, 
               label='LOESS smoothing', linestyle='-', zorder=5)

# Key events - vertical dashed lines
cxl_year = 2008
vision_year = 2016
ax.axvline(x=cxl_year, color='#F18F01', linestyle='--', linewidth=2.5, alpha=0.7, label='2008: CXL widely adopted')
ax.axvline(x=vision_year, color='#C73E1D', linestyle='--', linewidth=2.5, alpha=0.7, label='2016: Saudi Vision 2030')

# Mark 2002-2003 gap (real data artifact) - more visible
ax.axvspan(2001.5, 2003.5, alpha=0.15, color='#FFB6C6', zorder=1)

# Add annotation for 2002-2003 gap
ax.text(2002.5, ax.get_ylim()[1] * 0.95, 'No publications\nindexed 2002-2003', 
       ha='center', fontsize=9, style='italic', fontweight='bold',
       bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFB6C6', alpha=0.9, edgecolor='red', linewidth=1.5))

# Find peak publication year and add annotation
peak_year_data = pub_per_year[pub_per_year['year'] <= 2025]
peak_idx = peak_year_data['count'].idxmax()
peak_year = int(peak_year_data.loc[peak_idx, 'year'])
peak_count = int(peak_year_data.loc[peak_idx, 'count'])

# Add arrow annotation pointing to peak (2022)
ax.annotate(f'Peak: {peak_count} publications', 
           xy=(peak_year, peak_count), 
           xytext=(peak_year + 1.5, peak_count + 8),
           fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', 
                          color='black', lw=1.5))

# Labels and formatting
ax.set_xlabel('Year', fontsize=13, fontweight='bold')
ax.set_ylabel('Number of Publications', fontsize=13, fontweight='bold')
ax.set_title('Annual Publication Trend: Keratoconus in Saudi Arabia (2000–2025)',
             fontsize=15, fontweight='bold', pad=20)

# Grid
ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, axis='y')
ax.set_axisbelow(True)

# Set y-axis limits
ax.set_ylim(0, 58)

# Create custom legend entries
pink_patch = mpatches.Patch(color='#FFB6C6', alpha=0.15, label='Early period (sparse data)')
handles, labels = ax.get_legend_handles_labels()
handles.append(pink_patch)
labels.append('Early period (sparse data)')

# Update legend with custom patch
ax.legend(handles, labels, loc='upper left', fontsize=10, framealpha=0.95)

# Add statistics text box
shown_on_chart = total_records
stats_text = f'Total Publications: {total_records}\n' + \
             f'Time Period: 2000–2025\n' + \
             f'Trend: Smoothed LOESS fit'
ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, 
        fontsize=10, verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Set x-axis starting from 2000
ax.set_xlim(1999.5, 2025.5)
years = np.arange(2000, 2026, 2)
ax.set_xticks(years)

plt.tight_layout()

# Save figure
fig_file = base_path / "fig1_annual_trend_v3.png"
plt.savefig(fig_file, dpi=300, bbox_inches='tight', format='png')
print(f"\n✓ Figure saved to: {fig_file}")
print(f"  Resolution: 300 DPI")
print(f"  Format: PNG")
print(f"  X-axis range: 2000-2026 (sparse 1990s excluded to avoid negative y-intercept)")
print(f"  Y-axis range: 0-58 (with padding above peak)")
print(f"  Trend: LOESS smoothing with Savitzky-Goyal filter (2000-2025)")
print(f"  Peak annotation: {peak_year} ({peak_count} publications)")
print(f"\n✅ Figure improvements applied:")
print(f"  • Legend entry for early period (sparse data 2000-2003)")
print(f"  • LOESS curve stops at 2025 (does not extend to partial 2026)")
print(f"  • Arrow annotation pointing to peak: {peak_year} ({peak_count} pubs)")
print(f"  • Y-axis limits: 0-58 (padding added)")
print(f"  • 2002-2003 data gap marked and labeled")

plt.close()

print("\n" + "="*80)
print("✓ ANALYSIS COMPLETE")
print("="*80)
print(f"\nGenerated files:")
print(f"  1. KC_KSA_Table1_Summary.csv (descriptive statistics)")
print(f"  2. fig1_annual_trend.png (publication trend figure)")
