# processor/main.py

import os
import logging
import psycopg2
from minio import Minio

# -----------------------
# Configuration
# -----------------------
DB_URL = os.getenv("DATABASE_URL", "postgres://palabra:secret@localhost:5432/palabra")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "bookprep")
MINIO_USE_SSL = os.getenv("MINIO_SSL", "false").lower() == "true"

# -----------------------
# Logging
# -----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("processor")

# -----------------------
# Database connection
# -----------------------
try:
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    logger.info("Connected to Postgres")
except Exception as e:
    logger.error(f"Failed to connect to Postgres: {e}")
    raise

# -----------------------
# MinIO client
# -----------------------
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

# -----------------------
# Book processing stub
# -----------------------
def process_book(book_id, filename):
    """
    Stub function to process a book.
    Later this will:
      - Download file from MinIO
      - Extract text
      - Tokenize words
      - Insert/update words in the database
    """
    logger.info(f"Processing book {book_id}: {filename}")
    # TODO: implement actual processing
    pass

# -----------------------
# Main loop (placeholder)
# -----------------------
def main():
    logger.info("Processor started. Waiting for work...")
    # TODO: Replace this with real job queue or polling
    # For now we just demonstrate the setup
    while True:
        # Placeholder: break immediately for now
        break

if __name__ == "__main__":
    main()
