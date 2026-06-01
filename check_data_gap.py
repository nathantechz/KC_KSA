import pandas as pd
from pathlib import Path

base_path = Path("/Users/kqqs967/Library/CloudStorage/OneDrive-AZCollaboration/CORE/PhD/KC_KSA")
master_file = base_path / "KC_KSA_clean_master.csv"

df = pd.read_csv(master_file)
pub_per_year = df.groupby('year').size().reset_index(name='count').sort_values('year')

# Show 1995-2010 period
print("Publications 1995-2010 (checking for 2002-2003 gap):")
print(pub_per_year[(pub_per_year['year'] >= 1995) & (pub_per_year['year'] <= 2010)].to_string(index=False))

# Show 2024-2026 (current period)
print("\n\nPublications 2024-2026 (current period):")
print(pub_per_year[pub_per_year['year'] >= 2024].to_string(index=False))
