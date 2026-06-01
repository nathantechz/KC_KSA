import pandas as pd
from pathlib import Path

base_path = Path("/Users/kqqs967/Library/CloudStorage/OneDrive-AZCollaboration/CORE/PhD/KC_KSA")

master = pd.read_csv(base_path / "KC_KSA_kc_specific.csv")
scopus = pd.read_csv(
    base_path / "scopus_export_Jun 1-2026_c5292b85-5b5e-4737-b757-37ed3169cfab.csv",
    usecols=["DOI", "Author Keywords", "Index Keywords"],
)
scopus.columns = ["doi", "author_keywords", "index_keywords"]

# ── Normalise DOIs for joining ────────────────────────────────────────────────
master["_doi"] = master["doi"].str.strip().str.lower()
scopus["_doi"]  = scopus["doi"].str.strip().str.lower()

# ── Before stats ─────────────────────────────────────────────────────────────
before = master["keywords"].notna().sum()
print("=" * 55)
print(f"  Column inventory in KC_KSA_kc_specific.csv:")
print(f"    {list(master.columns)}")
print("=" * 55)
print(f"\n  Keyword columns found in master CSV : ['keywords']")
print(f"  Additional columns in Scopus export : ['Author Keywords', 'Index Keywords']")
print(f"\n  Papers WITH keywords BEFORE merge   : {before} / {len(master)}")

# ── Merge Scopus keyword columns in ──────────────────────────────────────────
df = master.merge(scopus[["_doi", "author_keywords", "index_keywords"]],
                  on="_doi", how="left")

# ── Combine all three keyword sources into one field ─────────────────────────
def combine_keywords(*sources):
    """Union of all semicolon-delimited keyword strings, deduped, lowercased."""
    seen = set()
    out  = []
    for src in sources:
        if pd.isna(src) or str(src).strip() == "":
            continue
        for kw in str(src).split(";"):
            kw = kw.strip().lower()
            if kw and kw not in seen:
                seen.add(kw)
                out.append(kw)
    return "; ".join(out) if out else None

df["all_keywords"] = df.apply(
    lambda r: combine_keywords(r["keywords"], r["author_keywords"], r["index_keywords"]),
    axis=1,
)

# ── After stats ───────────────────────────────────────────────────────────────
after = df["all_keywords"].notna().sum()
gained = after - before

print(f"\n  Sources merged into 'all_keywords'  : keywords + author_keywords + index_keywords")
print(f"  Papers WITH keywords AFTER  merge   : {after} / {len(df)}")
print(f"  Net gain                            : +{gained} papers now have keywords")
print(f"  Still missing keywords              : {len(df) - after} papers")
print()

# Breakdown of what each source contributed
only_orig   = df["keywords"].notna().sum()
only_author = df["author_keywords"].notna().sum()
only_index  = df["index_keywords"].notna().sum()
print(f"  Coverage by source:")
print(f"    keywords (original)  : {only_orig}")
print(f"    author_keywords      : {only_author}")
print(f"    index_keywords       : {only_index}")

# Papers that gained keywords purely from the new columns
gained_from_author = df[master["keywords"].isna() & df["author_keywords"].notna()].shape[0]
gained_from_index  = df[master["keywords"].isna() & df["index_keywords"].notna()].shape[0]
print(f"\n  Papers rescued by author_keywords   : {gained_from_author}")
print(f"  Papers rescued by index_keywords    : {gained_from_index}")
print()

# ── NLP fallback: extract title terms for papers still missing keywords ───────
from sklearn.feature_extraction.text import CountVectorizer

STOPWORDS = [
    'the','a','an','in','of','for','and','with','using','based',
    'study','analysis','saudi','arabia','patient','patients','case','report','review',
    'its','on','to','at','by','from','as','is','are','was','were','be','been',
    'this','that','their','our','we','it','or','not','no','vs',
]

missing_mask = df["all_keywords"].isna()
print(f"  Applying NLP title extraction to {missing_mask.sum()} papers...")

if missing_mask.sum() > 0:
    titles = df.loc[missing_mask, "title"].fillna("")
    vec = CountVectorizer(
        stop_words=STOPWORDS,
        ngram_range=(1, 2),   # unigrams + bigrams
        min_df=1,
        token_pattern=r"[a-zA-Z][a-zA-Z\-]{2,}",  # min 3-char alpha tokens
    )
    vec.fit(titles)
    X = vec.transform(titles)
    feature_names = vec.get_feature_names_out()

    extracted = []
    for i in range(X.shape[0]):
        row_terms = [feature_names[j] for j in X[i].nonzero()[1]]
        extracted.append("; ".join(row_terms) if row_terms else None)

    df.loc[missing_mask, "all_keywords"] = extracted

    after_nlp = df["all_keywords"].notna().sum()
    print(f"  Papers WITH keywords AFTER NLP fallback : {after_nlp} / {len(df)}")
    print(f"  Remaining missing                       : {len(df) - after_nlp}")
    print()
    for title, kws in zip(titles, extracted):
        print(f"  Title : {title}")
        print(f"  Terms : {kws}")
        print()

# ── Save enriched CSV ─────────────────────────────────────────────────────────
out_cols = [c for c in master.columns if c != "_doi"] + \
           ["author_keywords", "index_keywords", "all_keywords"]
df[out_cols].to_csv(base_path / "KC_KSA_kc_specific_enriched.csv", index=False)
print(f"  ✓ Saved: KC_KSA_kc_specific_enriched.csv")
print(f"    New columns added: author_keywords, index_keywords, all_keywords")
