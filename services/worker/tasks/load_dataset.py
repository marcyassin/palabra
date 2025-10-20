"""
Loads the generated lemma dataset CSV into Postgres `words` table.
"""

import os
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from worker.config.settings import DB_URL

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", PROJECT_ROOT / "language_datasets"))
SOURCE_LANG = os.getenv("SOURCE_LANG", "es")
TARGET_LANG = os.getenv("TARGET_LANG", "en")
BASE_FILENAME = f"{SOURCE_LANG}_to_{TARGET_LANG}_vocab_base.csv"
OUTPUT_GZ = OUTPUT_DIR / f"{BASE_FILENAME}.gz"


def load_dataset():
    print(f"📂 Loading dataset from {OUTPUT_GZ}...")
    df = pd.read_csv(OUTPUT_GZ)
    print(f"✅ Loaded {len(df)} rows. Inserting into database using SQLAlchemy...")

    engine = create_engine(DB_URL)

    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(
                text("""
                    INSERT INTO words (word, language, difficulty, zipf_score, created)
                    VALUES (:word, :language, :difficulty, :zipf_score, NOW())
                    ON CONFLICT (word, language)
                    DO UPDATE SET
                        difficulty = EXCLUDED.difficulty,
                        zipf_score = EXCLUDED.zipf_score;
                """),
                {
                    "word": row.word,
                    "language": row.language,
                    "difficulty": int(row.difficulty),
                    "zipf_score": float(row.zipf_score),
                },
            )

    print(f"💾 Upserted {len(df)} words into 'words' table.")
    print("✅ Done.")


if __name__ == "__main__":
    load_dataset()
