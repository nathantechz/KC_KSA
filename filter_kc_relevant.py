import pandas as pd
import numpy as np
from pathlib import Path

# Load the clean master dataset
base_path = Path("/Users/kqqs967/Library/CloudStorage/OneDrive-AZCollaboration/CORE/PhD/KC_KSA")
master_file = base_path / "KC_KSA_clean_master.csv"

print("Loading KC_KSA_clean_master.csv...")
df = pd.read_csv(master_file)

print(f"Total records: {len(df)}")

# Define KC-relevant keywords
kc_keywords = [
    'keratoconus',
    'corneal ectasia',
    'corneal crosslinking',
    'CXL',
    'corneal topography',
    'Pentacam',
    'keratoplasty',
    'DALK',
    'corneal transplant',
    'corneal collagen',
    'ectasia',
    'KC'
]

# Function to check if any keyword is in title or keywords
def is_kc_relevant(row):
    text = ""
    
    # Add title
    if pd.notna(row.get('title')):
        text += str(row['title']).lower() + " "
    
    # Add keywords
    if pd.notna(row.get('keywords')):
        text += str(row['keywords']).lower() + " "
    
    # Check for any keyword
    for keyword in kc_keywords:
        if keyword.lower() in text:
            return True
    
    return False

# Apply the function to create the kc_relevant column
print("\nProcessing records for KC relevance...")
df['kc_relevant'] = df.apply(is_kc_relevant, axis=1)

# Count results
kc_true = df['kc_relevant'].sum()
kc_false = len(df) - kc_true

print(f"\n" + "="*80)
print("KC RELEVANCE CLASSIFICATION RESULTS")
print("="*80)
print(f"\nTotal records processed: {len(df)}")
print(f"KC-specific records (kc_relevant=True): {kc_true} ({100*kc_true/len(df):.1f}%)")
print(f"Broad corneal records (kc_relevant=False): {kc_false} ({100*kc_false/len(df):.1f}%)")

# Export KC-specific records only
kc_specific_file = base_path / "KC_KSA_kc_specific.csv"
df_kc_specific = df[df['kc_relevant'] == True]
df_kc_specific.to_csv(kc_specific_file, index=False)
print(f"\n✓ KC-specific records exported to: {kc_specific_file}")
print(f"  Records: {len(df_kc_specific)}")

# Export all records with kc_relevant column
broad_file = base_path / "KC_KSA_broad_corneal.csv"
df.to_csv(broad_file, index=False)
print(f"\n✓ All records (with kc_relevant column) exported to: {broad_file}")
print(f"  Records: {len(df)}")

# Show sample of KC-specific records
print(f"\n" + "="*80)
print("SAMPLE OF KC-SPECIFIC RECORDS (first 5):")
print("="*80)
for idx, (i, row) in enumerate(df_kc_specific.head(5).iterrows()):
    print(f"\n{idx+1}. {row.get('title', 'N/A')[:80]}")
    print(f"   Keywords: {row.get('keywords', 'N/A')[:80]}")

print(f"\n" + "="*80)
print("✓ FILTERING COMPLETE")
print("="*80)
