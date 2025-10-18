"""
Builds the base Spanish vocabulary dataset using wordfreq.

Steps:
1. Fetch top N Spanish lemmas from wordfreq.
2. Assign CEFR-like difficulty levels (3–6) based on frequency rank.
3. Save as a compressed CSV (.csv.gz) ready for enrichment.

Output columns:
spanish_word,english_translation,definition_es,definition_en,difficulty
"""

import os
import math
import pandas as pd
from wordfreq import top_n_list

# --- Configuration ---
TOTAL_WORDS = 20_000
DIFFICULTY_DISTRIBUTION = {
    3: 0.25,  # B1
    4: 0.35,  # B2
    5: 0.25,  # C1
    6: 0.15,  # C2
}

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "dataset_builder/out")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "spanish_vocab_base.csv.gz")


def assign_difficulty(index: int) -> int:
    """
    Assign CEFR difficulty (3–6) based on position in the ranked frequency list.
    Note: This is a frequency-based approximation, not an official CEFR mapping.
    """
    total = 0
    for level, pct in DIFFICULTY_DISTRIBUTION.items():
        cutoff = math.floor(TOTAL_WORDS * pct)
        if index < total + cutoff:
            return level
        total += cutoff
    return 6


def build_dataset():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"📘 Generating top {TOTAL_WORDS} Spanish lemmas using wordfreq...")
    words = top_n_list("es", TOTAL_WORDS)
    print(f"✅ Retrieved {len(words)} unique lemmas")

    df = pd.DataFrame({
        "spanish_word": words,
        "english_translation": "",
        "definition_es": "",
        "definition_en": "",
        "difficulty": [assign_difficulty(i) for i in range(len(words))]
    })

    # Reorder for consistency
    df = df[["spanish_word", "english_translation", "definition_es", "definition_en", "difficulty"]]

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8", compression="gzip")
    print(f"✅ Saved compressed dataset to {OUTPUT_FILE} ({len(df)} rows)")


if __name__ == "__main__":
    build_dataset()
