import os
from dotenv import load_dotenv

load_dotenv()

# --- Database ---
DB_URL = os.getenv("DATABASE_URL")
SEED_DB_URL = os.getenv("SEED_DATABASE_URL")

# --- MinIO ---
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")
MINIO_USE_SSL = os.getenv("MINIO_SSL").lower() == "true"

# --- Redis ---
REDIS_URL = os.getenv("REDIS_URL")

# --- Language ---
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "es")
