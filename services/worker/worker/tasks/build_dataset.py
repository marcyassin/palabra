"""
Builds the core lemma dataset for Spanish (or any supported language).

Pipeline:
1. Get top N most frequent words from wordfreq.
2. Lemmatize and POS-tag using spaCy.
3. Deduplicate to unique lemmas.
4. Assign CEFR-like difficulty tiers (A1–C2).
5. Save to CSV and compressed CSV (.gz).

Columns:
word,pos,language,difficulty,zipf_score
"""

import os
import math
import pandas as pd
import spacy
from pathlib import Path
from wordfreq import top_n_list, word_frequency
from worker.nlp.sanitizers.spanish import clean_lemma

# --- Configuration ---
TOTAL_WORDS = int(os.getenv("TOTAL_WORDS", 50_000))
SOURCE_LANG = os.getenv("SOURCE_LANG", "es")
TARGET_LANG = os.getenv("TARGET_LANG", "en")

# The dataset should live in /language_datasets at the project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # palabra/
OUTPUT_DIR = PROJECT_ROOT / "language_datasets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_FILENAME = f"{SOURCE_LANG}_to_{TARGET_LANG}_vocab_base.csv"
OUTPUT_CSV = OUTPUT_DIR / BASE_FILENAME
OUTPUT_GZ = OUTPUT_DIR / f"{BASE_FILENAME}.gz"

# --- Load spaCy model ---
print(f"🧠 Loading spaCy model for '{SOURCE_LANG}'...")
try:
    nlp = spacy.load("es_core_news_lg")
except OSError:
    print("⚠️ Model not found. Run: python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_sm")


def assign_difficulty_by_rank(index: int, total: int) -> int:
    """Map rank percentile to CEFR-like difficulty levels."""
    pct = index / total
    if pct < 0.01:
        return 1  # A1
    elif pct < 0.03:
        return 2  # A2
    elif pct < 0.07:
        return 3  # B1
    elif pct < 0.15:
        return 4  # B2
    elif pct < 0.30:
        return 5  # C1
    return 6  # C2


def lemmatize(words):
    """Tokenize, lemmatize, and compute Zipf scores."""
    results = []
    for word in words:
        doc = nlp(word)
        token = doc[0]
        if token.is_alpha:
            lemma = clean_lemma(token.text, token.lemma_)
            # Skip malformed lemmas like "vender el" or multi-word artifacts
            if not lemma or " " in lemma or "el" in lemma.split():
                continue
            freq = word_frequency(word, SOURCE_LANG)
            zipf = 6 + math.log10(freq) if freq > 0 else 0
            results.append((lemma, token.pos_, zipf))
    return results


def build_dataset():
    print(f"📘 Generating top {TOTAL_WORDS:,} frequent words...")
    words = top_n_list(SOURCE_LANG, TOTAL_WORDS)
    lemma_data = lemmatize(words)

    # Deduplicate lemmas, keeping highest Zipf score
    lemma_dict = {}
    for lemma, pos, zipf in lemma_data:
        if lemma not in lemma_dict or zipf > lemma_dict[lemma]["zipf"]:
            lemma_dict[lemma] = {"pos": pos, "zipf": zipf}

    # Sort by Zipf (most frequent first)
    sorted_lemmas = sorted(lemma_dict.items(), key=lambda x: x[1]["zipf"], reverse=True)

    total = len(sorted_lemmas)
    data = [
        {
            "word": lemma,
            "pos": info["pos"],
            "language": SOURCE_LANG,
            "difficulty": assign_difficulty_by_rank(i, total),
            "zipf_score": info["zipf"],
        }
        for i, (lemma, info) in enumerate(sorted_lemmas)
    ]

    # Difficulty distribution
    print("\n📊 Difficulty distribution (CEFR-aligned):")
    counts = {lvl: 0 for lvl in range(1, 7)}
    for d in data:
        counts[d["difficulty"]] += 1
    labels = {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2"}
    for lvl in range(1, 7):
        pct = (counts[lvl] / total) * 100
        print(f"  {labels[lvl]} (Level {lvl}): {counts[lvl]:,} words ({pct:.1f}%)")

    # Write outputs
    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    df.to_csv(OUTPUT_GZ, index=False, encoding="utf-8", compression="gzip")

    print(f"\n💾 Saved plain CSV to {OUTPUT_CSV}")
    print(f"✅ Saved compressed CSV to {OUTPUT_GZ}")
    print(f"🌐 Languages: {SOURCE_LANG.upper()} → {TARGET_LANG.upper()}")
    print(f"✅ Total: {len(df)} words")


if __name__ == "__main__":
    build_dataset()
