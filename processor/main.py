# processor/main.py

import os
import logging
import re
import psycopg2
import nltk
from collections import Counter
from minio import Minio
from dotenv import load_dotenv
from tika import parser 
from io import BytesIO
from nltk.corpus import stopwords
from psycopg2.extras import execute_values

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgres://palabra:secret@localhost:5432/palabra")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "palabra")
MINIO_USE_SSL = os.getenv("MINIO_SSL", "false").lower() == "true"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("processor")
nltk.download('stopwords')

LANGUAGE_CODE = "es"

try:
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    logger.info("Connected to Postgres")
except Exception as e:
    logger.error(f"Failed to connect to Postgres: {e}")
    raise

try:
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_USE_SSL
    )
    if not minio_client.bucket_exists(MINIO_BUCKET):
        logger.error(f"Bucket '{MINIO_BUCKET}' does not exist!")
        raise RuntimeError(f"Bucket '{MINIO_BUCKET}' does not exist")
    logger.info(f"Connected to MinIO bucket '{MINIO_BUCKET}'")
except Exception as e:
    logger.error(f"Failed to connect to MinIO: {e}")
    raise


def process_book(book_id, filename):
    """
    Process a book end-to-end:
      1. Download file from MinIO
      2. Extract text via Tika
      3. Tokenize words and filter stopwords
      4. Insert words into `words` table if missing
      5. Insert word counts into `book_words` table
    """
    logger.info(f"Processing book {book_id}: {filename}")

    try:
        response = minio_client.get_object(MINIO_BUCKET, filename)
        data = BytesIO(response.read())
        response.close()
        response.release_conn()

        parsed = parser.from_buffer(data, serverEndpoint="http://localhost:9998/tika")
        text = parsed.get("content", "").strip()

        if not text:
            logger.warning(f"No text extracted from {filename}")
            return

        stop_words = set(stopwords.words("spanish"))
        words = re.findall(r'\b\w+\b', text.lower(), flags=re.UNICODE)
        words = [w for w in words if w.isalpha() and w not in stop_words]
        word_counts = Counter(words)

        logger.info(f"Book {book_id} contains {len(word_counts)} unique words")

        unique_words = [(word, LANGUAGE_CODE) for word in word_counts.keys()]

        with conn.cursor() as cur:
            # Insert words, ignore duplicates
            execute_values(
                cur,
                """
                INSERT INTO words (word, language)
                VALUES %s
                ON CONFLICT (word, language) DO NOTHING
                """,
                unique_words
            )

            # Fetch word IDs in bulk
            cur.execute(
                "SELECT id, word FROM words WHERE language = %s AND word = ANY(%s)",
                (LANGUAGE_CODE, list(word_counts.keys()))
            )
            word_id_map = {word: wid for wid, word in cur.fetchall()}

            # Prepare book_words insert
            book_word_values = [
                (book_id, word_id_map[word], count)
                for word, count in word_counts.items()
                if word in word_id_map
            ]

            execute_values(
                cur,
                """
                INSERT INTO book_words (book_id, word_id, count)
                VALUES %s
                ON CONFLICT (book_id, word_id) DO UPDATE
                SET count = EXCLUDED.count
                """,
                book_word_values
            )

        logger.info(f"Book {book_id} word counts inserted/updated successfully")

    except Exception as e:
        logger.error(f"Failed to process {filename}: {e}", exc_info=True)

def main():
    logger.info("Processor started. Running test extraction...")

    book_id = 1 
    filename = "f95b9737-fb6a-4feb-ba0c-07cf21732299-cixin.epub"

    try:
        process_book(book_id, filename)
    except Exception as e:
        logger.error(f"Failed to process book {filename}: {e}", exc_info=True)

if __name__ == "__main__":
    main()
