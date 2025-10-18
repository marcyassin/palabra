# processor/utils.py

import psycopg2
from psycopg2.extras import RealDictCursor
from minio import Minio
from minio.error import S3Error
import os
from ebooklib import epub
from bs4 import BeautifulSoup

# --------------------
# Database utilities
# --------------------
def get_postgres_conn():
    """Return a Postgres connection using environment variables."""
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "palabra"),
        user=os.getenv("POSTGRES_USER", "palabra"),
        password=os.getenv("POSTGRES_PASSWORD", "secret"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        cursor_factory=RealDictCursor
    )

# --------------------
# MinIO utilities
# --------------------
def get_minio_client():
    """Return a configured MinIO client."""
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    secure = os.getenv("MINIO_SSL", "false").lower() == "true"

    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
    return client

def download_file_from_minio(bucket_name: str, object_name: str, local_path: str):
    """Download a file from MinIO."""
    client = get_minio_client()
    try:
        client.fget_object(bucket_name, object_name, local_path)
    except S3Error as e:
        raise RuntimeError(f"MinIO download failed: {e}") from e

# --------------------
# EPUB / Text utilities
# --------------------
def extract_text_from_epub(file_path: str) -> str:
    """Extract plain text from an EPUB file."""
    book = epub.read_epub(file_path)
    text_content = []

    for item in book.get_items():
        if item.get_type() == epub.EpubHtml:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text_content.append(soup.get_text())

    return "\n".join(text_content)
