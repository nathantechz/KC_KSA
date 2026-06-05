"""
export_kc99_keywords_vos.py
===========================
Filters KC_KSA_kc_specific_enriched.csv to 2000–2025 (99 rows) and
exports a VOSviewer-compatible CSV for keyword co-occurrence analysis.

Keyword source  : all_keywords column (author + index + NLP title terms)
Output file     : kc99_for_vos.csv   (overwrites previous co-authorship file)
                  Columns: Authors | Title | Source title | Year | DOI |
                            Cited by | Author Keywords | Affiliations
                  but Keywords column contains the full merged set.

VOSviewer load:
  Create map → Based on bibliographic data →
  Read data from CSV file → Scopus format →
  Analysis type: Co-occurrence → Unit of analysis: All keywords
"""

import csv
import re
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(BASE, "KC_KSA_kc_specific_enriched.csv")
DST  = os.path.join(BASE, "kc99_for_vos.csv")

# ─────────────────────────────────────────────────────────────────────────────
# 1.  THESAURUS  – maps variants → canonical form (all lowercase)
#     Add more entries as needed; applied before noise filtering.
# ─────────────────────────────────────────────────────────────────────────────
THESAURUS = {
    # Keratoconus variants
    "kerotoconus": "keratoconus",
    "keratoconic": "keratoconus",

    # Cross-linking
    "corneal cross-linking": "corneal collagen cross-linking",
    "corneal crosslinking": "corneal collagen cross-linking",
    "cross-linking": "corneal collagen cross-linking",
    "crosslinking": "corneal collagen cross-linking",
    "cxl": "corneal collagen cross-linking",
    "cxl (corneal cross-linking)": "corneal collagen cross-linking",
    "accelerated corneal collagen cross-linking": "corneal collagen cross-linking",
    "epithelium off corneal collagen cross linking": "corneal collagen cross-linking",
    "iontophoresis assisted transepithelial corneal collagen cross linking": "transepithelial corneal collagen cross-linking",
    "corneal crosslinking (cxl)": "corneal collagen cross-linking",
    "riboflavin/uva cross-linking": "corneal collagen cross-linking",

    # Penetrating keratoplasty
    "pkp": "penetrating keratoplasty",
    "penetrating keratoplasty (pk)": "penetrating keratoplasty",
    "penetrating keratoplasty (pkp)": "penetrating keratoplasty",
    "keratoplasty, penetrating": "penetrating keratoplasty",

    # Deep anterior lamellar keratoplasty
    "dalk": "deep anterior lamellar keratoplasty",
    "deep anterior lamellar keratoplasty (dalk)": "deep anterior lamellar keratoplasty",
    "deep lamellar keratoplasty": "deep anterior lamellar keratoplasty",

    # DSAEK/DMEK
    "dsaek": "descemet stripping automated endothelial keratoplasty",
    "dmek": "descemet membrane endothelial keratoplasty",
    "descemet's stripping automated endothelial keratoplasty": "descemet stripping automated endothelial keratoplasty",

    # Keratoplasty generic
    "corneal transplantation": "keratoplasty",
    "corneal transplant": "keratoplasty",
    "cornea transplantation": "keratoplasty",
    "lamellar keratoplasty": "lamellar keratoplasty",

    # Intrastromal corneal ring segments
    "intrastromal corneal ring segments": "intracorneal ring segments",
    "intracorneal ring segment": "intracorneal ring segments",
    "icrs": "intracorneal ring segments",
    "intacs": "intracorneal ring segments",
    "keraring": "intracorneal ring segments",
    "ferrara rings": "intracorneal ring segments",

    # Implantable collamer lens
    "implantable collamer lens (icl)": "implantable collamer lens",
    "icl": "implantable collamer lens",
    "phakic intraocular lens": "phakic intraocular lens",
    "phakic intraocular lenses": "phakic intraocular lens",

    # Corneal ectasia
    "corneal ectasia": "corneal ectasia",
    "ectasia": "corneal ectasia",
    "post-lasik ectasia": "corneal ectasia",

    # Corneal topography / tomography
    "corneal tomography": "corneal topography",
    "pentacam": "scheimpflug imaging",
    "scheimpflug": "scheimpflug imaging",
    "scheimpflug tomography": "scheimpflug imaging",
    "scheimpflug camera": "scheimpflug imaging",
    "scheimpflug imaging system": "scheimpflug imaging",

    # Refractive surgery
    "laser in situ keratomileusis": "lasik",
    "laser-assisted in situ keratomileusis": "lasik",

    # Visual acuity abbreviations
    "bcva": "best corrected visual acuity",
    "ucva": "uncorrected visual acuity",
    "cdva": "corrected distance visual acuity",
    "corrected distance visual acuity": "best corrected visual acuity",
    "best spectacle corrected distance visual acuity": "best corrected visual acuity",

    # Artificial intelligence / machine learning
    "artificial intelligence": "artificial intelligence",
    "ai": "artificial intelligence",
    "machine learning": "machine learning",
    "deep learning": "deep learning",

    # Riboflavin
    "riboflavin/ultraviolet-a": "riboflavin",
    "riboflavin ultraviolet-a": "riboflavin",

    # Saudi Arabia geography (keep only as country)
    "ksa": "saudi arabia",
    "kingdom of saudi arabia": "saudi arabia",

    # Graft
    "graft failure": "corneal graft failure",
    "graft rejection": "corneal graft rejection",
    "allograft rejection": "corneal graft rejection",
    "graft survival": "corneal graft survival",

    # Genetic terms
    "vsx1": "vsx1 gene",
    "sod1": "sod1 gene",
    "znf469": "znf469 gene",

    # Misc normalisation
    "central corneal thickness (cct)": "central corneal thickness",
    "pachymetry": "corneal pachymetry",
    "confocal microscopy": "confocal microscopy",
    "optical coherence tomography": "optical coherence tomography",
    "tomography, optical coherence": "optical coherence tomography",
    "intraoperative optical coherence tomography": "intraoperative oct",
    "intraoperative optical coherent tomography": "intraoperative oct",
    "femtosecond laser": "femtosecond laser",
    "fs laser": "femtosecond laser",
    "lasers, excimer": "excimer laser",
    "excimer laser ablation": "excimer laser",
    "collagen cross-linking": "corneal collagen cross-linking",
    "cross linking reagent": "cross-linking reagents",
    "cross-linking reagents": "cross-linking reagents",
    "photosensitizing agent": "photosensitizing agents",
    "photosensitizing agents": "photosensitizing agents",
    "photochemotherapy": "photochemotherapy",
    "riboflavin/uva": "riboflavin",
    "uva": "ultraviolet-a",
    "ultraviolet rays": "ultraviolet-a",
    "ultraviolet radiation": "ultraviolet-a",
    "myopia (nearsightedness)": "myopia",
    "hypermetropia": "hyperopia",
    "intraocular lens": "intraocular lens",
    "intraocular lens power": "intraocular lens power calculation",
    "iop": "intraocular pressure",
    "intraocular pressure": "intraocular pressure",
    "endothelial cell": "corneal endothelial cells",
    "endothelial cell count": "corneal endothelial cells",
    "endothelial cell density": "corneal endothelial cells",
    "human corneal endothelial cells (hcecs)": "corneal endothelial cells",
    "cornea edema": "corneal edema",
    "cornea perforation": "corneal perforation",
    "cornea disease": "corneal disease",
    "cornea stroma": "corneal stroma",
    "cornea epithelium": "corneal epithelium",
    "descemet membrane": "descemet's membrane",
    "descemet's membrane (dm)": "descemet's membrane",
    "stromal-thinning disorders": "corneal ectasia",
    "pellucid marginal degeneration": "pellucid marginal degeneration",
    "macular corneal dystrophy": "corneal dystrophy",
    "fuchs endothelial dystrophy": "fuchs endothelial corneal dystrophy",
    "fuchs' endothelial corneal dystrophy": "fuchs endothelial corneal dystrophy",
    "corneal stromal dystrophy": "corneal dystrophy",
    "cornea dystrophy": "corneal dystrophy",
    "astigmatic keratotomy": "astigmatic keratotomy",
    "quality of life": "quality of life",
    "meta-analysis": "meta-analysis",
    "systematic review": "systematic review",
    "systematic review (topic)": "systematic review",
    "network meta-analysis": "network meta-analysis",
    "randomized controlled trial": "randomized controlled trial",
    "randomized controlled trial (topic)": "randomized controlled trial",
    "photorefractive keratectomy": "photorefractive keratectomy",
    "prk": "photorefractive keratectomy",
    "epikeratoplasty": "epikeratoplasty",
    "big bubble technique": "big bubble technique",
}

# ─────────────────────────────────────────────────────────────────────────────
# 2.  NOISE TERMS – generic terms to discard from co-occurrence analysis
# ─────────────────────────────────────────────────────────────────────────────
NOISE = {
    # Demographics / generic MeSH population terms
    "human", "humans", "female", "male", "adult", "adults", "aged",
    "child", "children", "adolescent", "middle aged", "young adult",
    "pediatric patient", "older adult", "groups by age",

    # Generic study design terms (low information value)
    "article", "review", "case report", "letter", "editorial",
    "retrospective study", "prospective study", "cohort analysis",
    "observational study", "comparative study", "controlled study",
    "cross-sectional study", "clinical study", "major clinical study",
    "clinical trial", "follow up", "follow-up studies",
    "clinical article", "clinical evaluation", "clinical feature",
    "clinical outcome", "retrospective studies", "prospective studies",
    "cross-sectional studies", "controlled clinical trial (topic)",

    # Generic procedural MeSH
    "procedures", "therapy", "diagnosis", "surgery", "drug therapy",
    "etiology", "pathology", "pathophysiology", "metabolism",
    "physiology", "epidemiology", "drug administration",
    "oral drug administration", "topical drug administration",
    "surgical technique",  # keep only specific surgical techniques

    # Generic outcomes / perioperative
    "treatment outcome", "visual acuity", "risk factor", "risk factors",
    "complication", "postoperative complication", "postoperative complications",
    "postoperative period", "perioperative period",
    "outcome assessment",

    # Generic data/methods
    "questionnaire", "data extraction", "electronic medical record",
    "medical record review",

    # Publishing / indexing artifacts
    "priority journal", "human tissue",

    # Very generic anatomy (too broad)
    "cornea",   # too generic — 'corneal' variants kept via specific terms

    # Miscellaneous noise
    "diseases", "disease", "knowledge base", "documentation",
    "staging",  # too generic
}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def clean_term(term: str) -> str:
    """Lowercase, strip brackets/parentheticals that are purely abbreviations."""
    term = term.strip().lower()
    # Remove trailing parenthetical if it's just an acronym  e.g. "(DALK)"
    term = re.sub(r'\s*\([A-Z0-9\-]{1,6}\)\s*$', '', term)
    return term.strip()


def apply_thesaurus(term: str) -> str:
    return THESAURUS.get(term, term)


def process_keywords(raw: str) -> list[str]:
    """Split, clean, deduplicate and filter a semicolon-delimited keyword string."""
    if not raw or str(raw).strip() in ("", "nan"):
        return []

    seen = {}   # canonical → first occurrence (preserves order)
    for part in str(raw).split(";"):
        term = clean_term(part)
        if not term:
            continue
        term = apply_thesaurus(term)
        if term in NOISE:
            continue
        if len(term) < 3:
            continue
        if term not in seen:
            seen[term] = True

    return list(seen.keys())

# ─────────────────────────────────────────────────────────────────────────────
# 3.  Read enriched CSV, filter 2000–2025, build VOSviewer output
# ─────────────────────────────────────────────────────────────────────────────

VOS_COLS = [
    "Authors",
    "Title",
    "Source title",
    "Year",
    "DOI",
    "Cited by",
    "Author Keywords",   # This is the merged, cleaned keyword field VOSviewer reads
    "Affiliations",
]

rows_out = []
missing_kw = []

with open(SRC, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            yr = int(str(row.get("year", "")).strip())
        except (ValueError, TypeError):
            continue
        if yr < 2000 or yr > 2025:
            continue

        # Keyword pipeline: use all_keywords (already merged from all sources)
        raw_kw = row.get("all_keywords", "") or ""
        kw_list = process_keywords(raw_kw)

        if not kw_list:
            missing_kw.append(row.get("title", "?")[:70])

        vos_row = {
            "Authors":          (row.get("authors") or "").strip(),
            "Title":            (row.get("title") or "").strip(),
            "Source title":     (row.get("journal") or "").strip(),
            "Year":             yr,
            "DOI":              (row.get("doi") or "").strip(),
            "Cited by":         (row.get("citations") or "0").strip() or "0",
            "Author Keywords":  "; ".join(kw_list),
            "Affiliations":     (row.get("affiliations") or "").strip(),
        }
        rows_out.append(vos_row)

rows_out.sort(key=lambda r: r["Year"])

with open(DST, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=VOS_COLS, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(rows_out)

# ─────────────────────────────────────────────────────────────────────────────
# 4.  Report
# ─────────────────────────────────────────────────────────────────────────────
total = len(rows_out)
with_kw = sum(1 for r in rows_out if r["Author Keywords"])
print(f"\n{'='*60}")
print(f"  Exported : {total} rows  →  {DST}")
print(f"  With keywords : {with_kw} / {total}")
print(f"  Missing keywords : {total - with_kw}")
if missing_kw:
    print("\n  Papers with no keywords after processing:")
    for t in missing_kw:
        print(f"    • {t}")

# Keyword frequency summary
from collections import Counter
all_terms = []
for r in rows_out:
    all_terms.extend([k.strip() for k in r["Author Keywords"].split(";") if k.strip()])
freq = Counter(all_terms)
print(f"\n  Total unique keywords : {len(freq)}")
print(f"  Top 30 most frequent keywords:")
print(f"  {'Keyword':<50} Count")
print(f"  {'-'*58}")
for term, cnt in freq.most_common(30):
    print(f"  {term:<50} {cnt}")
print(f"{'='*60}\n")
