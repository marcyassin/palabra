"""
Builds a lemma-based vocabulary dataset for a given source language using wordfreq and spaCy.

Pipeline:
1. Get top N most frequent words from wordfreq.
2. Lemmatize and POS-tag using spaCy.
3. Aggregate frequencies and collect all inflected forms per lemma.
4. Assign CEFR-like difficulty using rank-based proportional mapping (A1–C2).
5. Drop lemmas that have only one surface form (non-inflecting words).
6. Save both plain CSV and compressed CSV (.csv.gz).

Output columns:
lemma,pos,forms,target_translation,definition_source,definition_target,example_source,example_target,difficulty,zipf
"""

import os
import math
import pandas as pd
from pathlib import Path
from collections import defaultdict
from wordfreq import top_n_list, word_frequency
import spacy

# --- Configuration ---
TOTAL_WORDS = int(os.getenv("TOTAL_WORDS", 100_000))
SOURCE_LANG = os.getenv("SOURCE_LANG", "es")
TARGET_LANG = os.getenv("TARGET_LANG", "en")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", PROJECT_ROOT / "language_datasets"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_FILENAME = f"{SOURCE_LANG}_to_{TARGET_LANG}_vocab_base.csv"
OUTPUT_CSV = OUTPUT_DIR / BASE_FILENAME
OUTPUT_GZ = OUTPUT_DIR / f"{BASE_FILENAME}.gz"

# --- Load spaCy model ---
print(f"🧠 Loading spaCy model for '{SOURCE_LANG}'...")
if SOURCE_LANG.startswith("es"):
    try:
        nlp = spacy.load("es_core_news_lg")
    except OSError:
        print("⚠️ Transformer model not found. Run:")
        print("python -m spacy download es_core_news_lg")
        nlp = spacy.load("es_core_news_lg")
else:
    raise ValueError(f"No spaCy model configured for language '{SOURCE_LANG}'")

# --- Helper functions ---
def assign_difficulty_by_rank(index: int, total_words: int) -> int:
    """
    Assign CEFR-like difficulty (1–6) based on frequency rank,
    using flattened proportions for better coverage.
    """
    pct = index / total_words
    if pct < 0.02:      # top 2%
        return 1  # A1
    elif pct < 0.06:    # next 4%
        return 2  # A2
    elif pct < 0.14:    # next 8%
        return 3  # B1
    elif pct < 0.30:    # next 16%
        return 4  # B2
    elif pct < 0.55:    # next 25%
        return 5  # C1
    else:
        return 6  # C2


def lemmatize_words(words):
    """
    Lemmatize and POS-tag the list of words using spaCy.
    Returns a list of tuples: (original_word, lemma, pos)
    """
    results = []
    batch_size = 1000
    for i in range(0, len(words), batch_size):
        doc = nlp(" ".join(words[i:i + batch_size]))
        for token in doc:
            if token.is_alpha:
                results.append((token.text.lower(), token.lemma_.lower(), token.pos_))
    return results


def build_dataset():
    print(f"📘 Generating top {TOTAL_WORDS:,} frequent words for '{SOURCE_LANG}' using wordfreq...")
    words = top_n_list(SOURCE_LANG, TOTAL_WORDS)
    print(f"✅ Retrieved {len(words)} tokens. Beginning lemmatization...")

    lemma_data = lemmatize_words(words)
    print(f"🔤 Lemmatized {len(lemma_data)} tokens.")

    # --- Aggregate frequencies and forms across lemmas ---
    lemma_freqs = defaultdict(float)
    lemma_pos = {}
    lemma_forms = defaultdict(set)

    print("📊 Aggregating lemma frequencies and forms...")
    for orig, lemma, pos in lemma_data:
        freq = word_frequency(orig, SOURCE_LANG)
        lemma_freqs[lemma] += freq
        lemma_pos[lemma] = pos
        lemma_forms[lemma].add(orig)

    # Convert to list of tuples
    aggregated = [
        (
            lemma,
            lemma_pos[lemma],
            ", ".join(sorted(lemma_forms[lemma])),
            lemma_freqs[lemma],
        )
        for lemma in lemma_freqs
    ]

    # Build DataFrame
    df = pd.DataFrame(aggregated, columns=["lemma", "pos", "forms", "freq"])

    # Drop lemmas with only one form (optional cleanup)
    df["form_count"] = df["forms"].apply(lambda f: len(f.split(",")))
    before_count = len(df)
    df = df[df["form_count"] > 1].drop(columns=["form_count"])
    after_count = len(df)
    print(f"🧹 Dropped {before_count - after_count:,} lemmas with only one form.")

    # Compute Zipf score from aggregated frequency
    df["zipf"] = df["freq"].apply(lambda f: 6 + math.log10(f) if f > 0 else 0)

    # Sort by Zipf (descending = most frequent first)
    df.sort_values(by="zipf", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Assign difficulty based on rank
    df["difficulty"] = [assign_difficulty_by_rank(i, len(df)) for i in range(len(df))]

    # Fill in placeholders for enrichment
    df["target_translation"] = ""
    df["definition_source"] = ""
    df["definition_target"] = ""
    df["example_source"] = ""
    df["example_target"] = ""

    # Reorder columns
    df = df[
        [
            "lemma",
            "pos",
            "forms",
            "target_translation",
            "definition_source",
            "definition_target",
            "example_source",
            "example_target",
            "difficulty",
            "zipf",
        ]
    ]

    # Difficulty breakdown
    counts = df["difficulty"].value_counts().sort_index()
    print("\n📊 Difficulty distribution (CEFR-aligned):")
    for level, count in counts.items():
        label = {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2"}[level]
        pct = (count / len(df)) * 100
        print(f"  {label} (Level {level}): {count:,} words ({pct:.1f}%)")

    # Save both formats
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    df.to_csv(OUTPUT_GZ, index=False, encoding="utf-8", compression="gzip")

    print(f"\n💾 Saved plain CSV to {OUTPUT_CSV}")
    print(f"✅ Saved compressed CSV to {OUTPUT_GZ}")
    print(f"🌐 Languages: {SOURCE_LANG.upper()} → {TARGET_LANG.upper()}")
    print(f"📊 Rows: {len(df)} | Unique lemmas | Sample:\n{df.head(10).to_markdown(index=False)}")


if __name__ == "__main__":
    build_dataset()
