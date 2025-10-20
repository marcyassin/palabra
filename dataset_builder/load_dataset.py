"""
Loads the generated lemma dataset CSV into Postgres `words` table.
"""

import os
import psycopg
import pandas as pd
from config.settings import DB_URL
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", PROJECT_ROOT / "language_datasets"))
SOURCE_LANG = os.getenv("SOURCE_LANG", "es")
TARGET_LANG = os.getenv("TARGET_LANG", "en")
BASE_FILENAME = f"{SOURCE_LANG}_to_{TARGET_LANG}_vocab_base.csv"
OUTPUT_GZ = OUTPUT_DIR / f"{BASE_FILENAME}.gz"


def load_dataset():
    print(f"📂 Loading dataset from {OUTPUT_GZ}...")
    df = pd.read_csv(OUTPUT_GZ)
    print(f"✅ Loaded {len(df)} rows. Inserting into database...")

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                cur.execute("""
                    INSERT INTO words (word, language, difficulty, zipf_score, created)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (word, language)
                    DO UPDATE SET
                        difficulty = EXCLUDED.difficulty,
                        zipf_score = EXCLUDED.zipf_score;
                """, (row.word, row.language, int(row.difficulty), float(row.zipf_score)))
        conn.commit()

    print(f"💾 Upserted {len(df)} words into 'words' table.")
    print("✅ Done.")


if __name__ == "__main__":
    load_dataset()
