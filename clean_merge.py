import pandas as pd
import os
from pathlib import Path

# Define file paths
base_path = Path("/Users/kqqs967/Library/CloudStorage/OneDrive-AZCollaboration/CORE/PhD/KC_KSA")
pubmed_file = base_path / "pubmed_csv-keratoconu-set.csv"
scopus_file = base_path / "scopus_export_Jun 1-2026_c5292b85-5b5e-4737-b757-37ed3169cfab.csv"

# Read both files
print("Reading PubMed CSV...")
pubmed = pd.read_csv(pubmed_file)
print(f"PubMed records: {len(pubmed)}")

print("\nReading Scopus CSV...")
scopus = pd.read_csv(scopus_file)
print(f"Scopus records: {len(scopus)}")

# Display column names
print("\nPubMed columns:", pubmed.columns.tolist())
print("\nScopus columns:", scopus.columns.tolist())

# Create normalized dataframes with consistent columns
# Target columns: title, year, authors, affiliations, journal, citations, keywords

# Process PubMed
pubmed_clean = pd.DataFrame({
    'title': pubmed['Title'],
    'year': pubmed['Publication Year'],
    'authors': pubmed['Authors'],
    'affiliations': '',  # PubMed CSV doesn't have affiliation data
    'journal': pubmed['Journal/Book'],
    'citations': '',  # Will extract from Citation field if available
    'keywords': '',  # Not available in PubMed CSV
    'doi': pubmed['DOI'],
    'source': 'PubMed',
    'pmid': pubmed['PMID']
})

# Process Scopus
scopus_clean = pd.DataFrame({
    'title': scopus['Title'],
    'year': scopus['Year'],
    'authors': scopus['Authors'],
    'affiliations': scopus['Affiliations'],
    'journal': scopus['Source title'],
    'citations': scopus['Cited by'],
    'keywords': scopus['Author Keywords'],
    'doi': scopus['DOI'],
    'source': 'Scopus',
    'pmid': scopus['PubMed ID']
})

# Combine datasets
combined = pd.concat([pubmed_clean, scopus_clean], ignore_index=True)
print(f"\nCombined records: {len(combined)}")

# Remove duplicates by DOI (keeping first occurrence)
print("\nRemoving duplicates by DOI...")
before_doi_dedup = len(combined)
combined = combined.drop_duplicates(subset=['doi'], keep='first')
print(f"Removed {before_doi_dedup - len(combined)} DOI duplicates")

# Remove duplicates by Title (case-insensitive)
print("Removing duplicates by Title...")
before_title_dedup = len(combined)
combined['title_normalized'] = combined['title'].str.lower().str.strip()
combined = combined.drop_duplicates(subset=['title_normalized'], keep='first')
combined = combined.drop('title_normalized', axis=1)
print(f"Removed {before_title_dedup - len(combined)} title duplicates")

# Flag records with missing affiliations
combined['affiliation_missing'] = combined['affiliations'].isna() | (combined['affiliations'] == '')
missing_affiliation_count = combined['affiliation_missing'].sum()
print(f"\nRecords with missing affiliations: {missing_affiliation_count}")

# Filter for Saudi papers only
# Look for "Saudi" in affiliations, journal, or authors with known Saudi institutions
saudi_keywords = [
    'saudi', 'king faisal', 'king abdulaziz', 'king saud', 'jeddah', 'riyadh', 'dammam', 
    'medina', 'abha', 'taibah', 'umm al-qura', 'qassim', 'jazan', 'hafr', 'prince mohd bin fahd'
]

def is_saudi_paper(row):
    # Check affiliations
    if pd.notna(row['affiliations']) and row['affiliations'] != '':
        aff_lower = str(row['affiliations']).lower()
        if any(keyword in aff_lower for keyword in saudi_keywords):
            return True
    
    # Check authors
    if pd.notna(row['authors']) and row['authors'] != '':
        authors_lower = str(row['authors']).lower()
        if any(keyword in authors_lower for keyword in saudi_keywords):
            return True
    
    # Check journal
    if pd.notna(row['journal']) and row['journal'] != '':
        journal_lower = str(row['journal']).lower()
        if any(keyword in journal_lower for keyword in saudi_keywords):
            return True
    
    return False

print("\nFiltering for Saudi papers...")
before_filter = len(combined)
combined['is_saudi'] = combined.apply(is_saudi_paper, axis=1)
saudi_papers = combined[combined['is_saudi']].copy()
print(f"Saudi papers identified: {len(saudi_papers)} out of {before_filter}")
print(f"Removed {before_filter - len(saudi_papers)} non-Saudi papers")

# Drop helper column
saudi_papers = saudi_papers.drop('is_saudi', axis=1)

# Create final clean dataset with required columns
final_clean = saudi_papers[[
    'title', 'year', 'authors', 'affiliations', 'journal', 'citations', 'keywords',
    'affiliation_missing', 'source', 'doi'
]].copy()

# Replace NaN with empty strings for better readability
final_clean = final_clean.fillna('')

# Convert citations to integers where possible
final_clean['citations'] = pd.to_numeric(final_clean['citations'], errors='coerce').fillna(0).astype(int)

# Sort by year descending
final_clean = final_clean.sort_values('year', ascending=False, na_position='last')

print(f"\nFinal clean dataset: {len(final_clean)} records")

# Save to CSV
output_file = base_path / "KC_KSA_clean_master.csv"
final_clean.to_csv(output_file, index=False, quotechar='"', quoting=1)
print(f"\n✓ Clean master spreadsheet saved to: {output_file}")

# Summary statistics
print("\n" + "="*60)
print("SUMMARY STATISTICS")
print("="*60)
print(f"Total records: {len(final_clean)}")
print(f"Records with missing affiliations: {final_clean['affiliation_missing'].sum()}")
print(f"Date range: {final_clean['year'].min()} - {final_clean['year'].max()}")
print(f"Average citations: {final_clean['citations'].mean():.1f}")
print(f"\nSources:")
print(final_clean['source'].value_counts())

# Create flagged report
flagged = final_clean[final_clean['affiliation_missing'] == True][['title', 'year', 'journal', 'source']].copy()
if len(flagged) > 0:
    flagged_file = base_path / "KC_KSA_flagged_missing_affiliations.csv"
    flagged.to_csv(flagged_file, index=False)
    print(f"\n⚠ Records with missing affiliations saved to: {flagged_file}")
