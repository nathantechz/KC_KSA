"""
Export kc99_for_vos.csv
-----------------------
Filters KC_KSA_kc_specific.csv to 2000 <= year <= 2025 (99 rows)
and writes a CSV formatted for VOSviewer co-authorship analysis.

VOSviewer accepts a CSV/RIS with at minimum:
  Authors (AU), Title (TI), Source title (SO), Year (PY),
  DOI, Citations (TC).

The column names used here match the VOSviewer "Web of Science" /
"Scopus" CSV field mapping so the file can be loaded via
  Create → Based on bibliographic data → Read data from CSV file.
"""

import csv
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(BASE, "KC_KSA_kc_specific.csv")
DST  = os.path.join(BASE, "kc99_for_vos.csv")

# VOSviewer column headers (Scopus-style CSV mapping)
VOS_COLS = [
    "Authors",          # AU  – semicolon-separated full names
    "Title",            # TI
    "Source title",     # SO  – journal name
    "Year",             # PY
    "DOI",              # DI
    "Cited by",         # TC  – citation count
    "Author Keywords",  # DE  – semicolon-separated keywords
    "Affiliations",     # C1  – author affiliations
]

rows_out = []

with open(SRC, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            yr = int(row["year"])
        except (ValueError, TypeError):
            continue
        if yr < 2000 or yr > 2025:
            continue

        # ---------- normalise author string ----------
        # source stores "Surname F.; Surname2 G." or "Surname F, Surname2 G."
        authors_raw = row.get("authors", "").strip()
        # VOSviewer expects semicolons; already semicoloned in most Scopus rows
        authors = authors_raw.replace(" and ", "; ") if authors_raw else ""

        # ---------- normalise keywords ----------
        kw_raw = row.get("keywords", "").strip()
        # Already semicoloned in source
        keywords = kw_raw if kw_raw else ""

        vos_row = {
            "Authors":          authors,
            "Title":            row.get("title", "").strip(),
            "Source title":     row.get("journal", "").strip(),
            "Year":             yr,
            "DOI":              row.get("doi", "").strip(),
            "Cited by":         row.get("citations", "0").strip() or "0",
            "Author Keywords":  keywords,
            "Affiliations":     row.get("affiliations", "").strip(),
        }
        rows_out.append(vos_row)

rows_out.sort(key=lambda r: r["Year"])

with open(DST, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=VOS_COLS, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(rows_out)

print(f"Exported {len(rows_out)} rows → {DST}")

# Quick year distribution check
from collections import Counter
dist = Counter(r["Year"] for r in rows_out)
for yr in sorted(dist):
    print(f"  {yr}: {dist[yr]} paper(s)")
