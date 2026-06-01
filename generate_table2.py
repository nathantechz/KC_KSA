import pandas as pd
from pathlib import Path

# Load KC-specific dataset
base_path = Path("/Users/kqqs967/Library/CloudStorage/OneDrive-AZCollaboration/CORE/PhD/KC_KSA")
kc_specific_file = base_path / "KC_KSA_kc_specific.csv"

print("Loading KC_KSA_kc_specific.csv...")
df = pd.read_csv(kc_specific_file)

print(f"Total KC-specific records: {len(df)}")

# Sort by citations descending and get top 11 (to account for exclusion)
top_11 = df.nlargest(11, 'citations').copy()

# Identify and exclude the Wagoner 1997 outlier (highest cited general corneal review)
# This paper has 499 citations vs next highest at 109 - methodologically valid exclusion
wagoner_mask = (top_11['year'] == 1997) & (top_11['citations'] == 499)
top_10_filtered = top_11[~wagoner_mask].head(10).copy()

# Extract first author from authors field (before semicolon)
def get_first_author(authors_str):
    if pd.isna(authors_str) or authors_str == '':
        return ''
    first = str(authors_str).split(';')[0].strip()
    return first

top_10_filtered['first_author'] = top_10_filtered['authors'].apply(get_first_author)

# Truncate title to 90 characters
top_10_filtered['title'] = top_10_filtered['title'].apply(lambda x: str(x)[:90] if pd.notna(x) else '')

# Select and rename columns
top_10_export = top_10_filtered[['title', 'year', 'journal', 'citations', 'first_author']].copy()
top_10_export.columns = ['Title', 'Year', 'Journal', 'Citations', 'First Author']

# Add rank column at the beginning
top_10_export.insert(0, 'Rank', range(1, len(top_10_export) + 1))

# Reset index for clean output
top_10_export = top_10_export.reset_index(drop=True)

print("\n" + "="*120)
print("TABLE 2: TOP 10 MOST-CITED KC-SPECIFIC PAPERS FROM SAUDI ARABIA")
print("="*120)
print(top_10_export.to_string(index=False))

# Save to CSV
output_file = base_path / "KC_KSA_Table2_Top10Cited_v2.csv"
top_10_export.to_csv(output_file, index=False, quotechar='"', quoting=1)
print(f"\n✓ Table 2 (v2) saved to: {output_file}")

# Print summary
print(f"\nSummary Statistics:")
print(f"  Total citations in Top 10: {top_10_export['Citations'].sum()}")
print(f"  Average citations per paper: {top_10_export['Citations'].mean():.1f}")
print(f"  Citation range: {top_10_export['Citations'].min()}-{top_10_export['Citations'].max()}")
print(f"  Year range: {top_10_export['Year'].min()}-{top_10_export['Year'].max()}")

# Save footnote explanation
footnote_text = """TABLE 2 FOOTNOTES:
================================================================================

* Exclusion of Citation Outlier:
  The highest-cited record in the KC-specific dataset was Wagoner et al. (1997, 
  n=499 citations), a general corneal injury review published by KKESH. This 
  paper represents a 4.5× gap over the next-highest cited paper (n=109) and 
  predates the thematic focus on keratoconus-specific research. This outlier has 
  been excluded from citation metrics and included as a historical reference 
  instead. This exclusion strengthens the validity of citation analysis by 
  focusing on papers within the study's scope and prevents one seminal review 
  from dominating aggregate statistics.

* Broad CXL Application (Rank 10):
  The paper ranked 10 (Anwar et al., 2011) applies corneal crosslinking to 
  infectious keratitis treatment rather than KC management. It is included here 
  because CXL is a major KC therapeutic innovation. This demonstrates the broader 
  translational impact of KC research on corneal disease management.

================================================================================
"""

footnote_file = base_path / "KC_KSA_Table2_Footnotes.txt"
with open(footnote_file, 'w') as f:
    f.write(footnote_text)

print(f"\n✓ Footnotes saved to: {footnote_file}")

print("\n" + "="*120)
print("✓ METHODOLOGY NOTE")
print("="*120)
print("\nWagoner et al. (1997) - 499 citations - EXCLUDED")
print("  Reason: Citation outlier (4.5× gap), general corneal injuries, predates KC-specific scope")
print("  Location: Referenced in footnote as historical context")
print("\nResult: Table 2 now reflects KC-specific publication impact without outlier skew")
print("="*120)
