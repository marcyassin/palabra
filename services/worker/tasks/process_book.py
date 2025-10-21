from rq import get_current_job
from worker.utils.logger import get_logger
from worker.storage.minio_client import get_minio_client
from worker.nlp.extractor import extract_words_from_buffer
from worker.nlp.sanitizers.spanish import clean_lemma
from worker.config.settings import MINIO_BUCKET, LANGUAGE_CODE
from worker.db.connection import engine
from sqlalchemy import text
import spacy

logger = get_logger(__name__)

# --- Load spaCy model once globally ---
logger.info("🧠 Loading spaCy model for Spanish...")
try:
    nlp = spacy.load("es_core_news_lg", disable=["ner"])
except OSError:
    logger.warning("⚠️ Model not found. Run: python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_sm", disable=["ner"])


def process_book(book_id, filename):
    """
    Extract, lemmatize, and persist words from a book file.
    Uses nlp.pipe for efficient batch lemmatization.
    """
    job = get_current_job()
    if job:
        logger.info(f"🚀 Starting RQ job {job.id} for book {book_id}")

    minio_client = get_minio_client()
    logger.info(f"📘 Processing book {book_id}: {filename}")

    # --- Retrieve book content from MinIO ---
    response = minio_client.get_object(MINIO_BUCKET, filename)
    data = response.read()
    response.close()
    response.release_conn()

    # --- Extract tokens ---
    word_counts, language = extract_words_from_buffer(data)
    logger.info(f"🔤 Extracted {len(word_counts)} unique tokens before lemmatization")

    if not word_counts:
        logger.warning("⚠️ No words extracted. Skipping book.")
        return

    # --- Lemmatize in batches using spaCy's nlp.pipe() ---
    lemma_counter = {}
    batch_size = 1000

    for docs in nlp.pipe(word_counts.keys(), batch_size=batch_size):
        token = docs[0]
        if not token.is_alpha:
            continue
        lemma = clean_lemma(token.text, token.lemma_)
        if not lemma or " " in lemma or "el" in lemma.split():
            continue
        lemma_counter[lemma] = lemma_counter.get(lemma, 0) + word_counts[token.text]

    logger.info(f"🧩 Reduced to {len(lemma_counter)} unique lemmas after normalization")

    if not lemma_counter:
        logger.warning("⚠️ No valid lemmas after cleaning. Skipping DB update.")
        return

    # --- Insert or update database records ---
    with engine.begin() as conn:
        # Upsert words
        conn.execute(
            text("""
                INSERT INTO words (word, language)
                VALUES (:word, :lang)
                ON CONFLICT (word, language) DO NOTHING
            """),
            [{"word": w, "lang": LANGUAGE_CODE} for w in lemma_counter],
        )

        # Get word IDs for this language
        rows = conn.execute(
            text("SELECT id, word FROM words WHERE language=:lang AND word=ANY(:words)"),
            {"lang": LANGUAGE_CODE, "words": list(lemma_counter.keys())},
        ).fetchall()
        id_map = {r.word: r.id for r in rows}

        # Upsert word frequencies for the book
        conn.execute(
            text("""
                INSERT INTO book_words (book_id, word_id, count)
                VALUES (:book, :word_id, :count)
                ON CONFLICT (book_id, word_id)
                DO UPDATE SET count = EXCLUDED.count
            """),
            [
                {"book": book_id, "word_id": id_map[w], "count": c}
                for w, c in lemma_counter.items() if w in id_map
            ],
        )

    if job:
        job.meta["status"] = "completed"
        job.save_meta()
        logger.info(f"🏁 RQ job {job.id} completed successfully.")

    logger.info(f"✅ Book {book_id} processed successfully.")
    logger.info(f"🌐 Language detected: {language}")
