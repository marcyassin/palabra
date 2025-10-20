from worker.utils.logger import get_logger
from worker.storage.minio_client import get_minio_client
from worker.nlp.extractor import extract_words_from_file
from worker.config.settings import MINIO_BUCKET, LANGUAGE_CODE
from worker.db.connection import engine
from sqlalchemy import text

logger = get_logger(__name__)

def process_book(book_id, filename):
    minio_client = get_minio_client()
    logger.info(f"Processing book {book_id}: {filename}")

    response = minio_client.get_object(MINIO_BUCKET, filename)
    data = response.read()
    response.close(); response.release_conn()

    word_counts, language = extract_words_from_file(data)
    logger.info(f"{len(word_counts)} unique words extracted")

    # Use SQLAlchemy connection for now (raw SQL ok here)
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO words (word, language)
            VALUES (:word, :lang)
            ON CONFLICT (word, language) DO NOTHING
        """), [{"word": w, "lang": LANGUAGE_CODE} for w in word_counts])

        rows = conn.execute(
            text("SELECT id, word FROM words WHERE language=:lang AND word=ANY(:words)"),
            {"lang": LANGUAGE_CODE, "words": list(word_counts.keys())}
        ).fetchall()
        id_map = {r.word: r.id for r in rows}

        conn.execute(text("""
            INSERT INTO book_words (book_id, word_id, count)
            VALUES (:book, :word_id, :count)
            ON CONFLICT (book_id, word_id) DO UPDATE SET count = EXCLUDED.count
        """), [
            {"book": book_id, "word_id": id_map[w], "count": c}
            for w, c in word_counts.items() if w in id_map
        ])

    logger.info(f"Book {book_id} processed successfully.")
    logger.info(f"language detected: {language}")
