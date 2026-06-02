"""
Convert KC_KSA_clean_master.csv (367 records) to RIS format for VOSviewer.

RIS tags used:
  TY  - JOUR
  TI  - title
  AU  - author (one line per author)
  PY  - year
  SO  - journal/source
  TC  - times cited
  KW  - keyword (one line per keyword, split on semicolon)
  AD  - affiliations
  ER  - end of record
"""

import csv
import os

INPUT_FILE  = "KC_KSA_clean_master.csv"
OUTPUT_FILE = "KC_KSA_master.ris"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH  = os.path.join(SCRIPT_DIR, INPUT_FILE)
OUTPUT_PATH = os.path.join(SCRIPT_DIR, OUTPUT_FILE)


def clean(value: str) -> str:
    """Strip whitespace and surrounding quotes."""
    return value.strip().strip('"').strip()


def write_ris(records, out_path):
    written = 0
    skipped = 0

    with open(out_path, "w", encoding="utf-8") as fout:
        for i, row in enumerate(records, start=1):
            title       = clean(row.get("title", ""))
            year        = clean(row.get("year", ""))
            authors_raw = clean(row.get("authors", ""))
            affil       = clean(row.get("affiliations", ""))
            journal     = clean(row.get("journal", ""))
            citations   = clean(row.get("citations", "0"))
            keywords_raw = clean(row.get("keywords", ""))

            if not title:
                print(f"  [SKIP row {i}] No title found.")
                skipped += 1
                continue

            # ---- TY ----
            fout.write("TY  - JOUR\n")

            # ---- TI ----
            fout.write(f"TI  - {title}\n")

            # ---- AU  (one per line, split on semicolons) ----
            if authors_raw:
                authors = [a.strip() for a in authors_raw.split(";") if a.strip()]
                for author in authors:
                    fout.write(f"AU  - {author}\n")

            # ---- PY ----
            if year:
                fout.write(f"PY  - {year}\n")

            # ---- SO ----
            if journal:
                fout.write(f"SO  - {journal}\n")

            # ---- TC ----
            if citations:
                fout.write(f"TC  - {citations}\n")

            # ---- KW  (one per line, split on semicolons) ----
            if keywords_raw:
                keywords = [k.strip() for k in keywords_raw.split(";") if k.strip()]
                for kw in keywords:
                    fout.write(f"KW  - {kw}\n")

            # ---- AD ----
            if affil:
                fout.write(f"AD  - {affil}\n")

            # ---- ER ----
            fout.write("ER  - \n\n")
            written += 1

    return written, skipped


def main():
    print(f"Reading: {INPUT_PATH}")
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    records = []
    with open(INPUT_PATH, "r", encoding="utf-8-sig") as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            records.append(row)

    total = len(records)
    print(f"Total records loaded: {total}")

    written, skipped = write_ris(records, OUTPUT_PATH)

    print(f"\nDone!")
    print(f"  Records written : {written}")
    print(f"  Records skipped : {skipped}")
    print(f"  Output file     : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
