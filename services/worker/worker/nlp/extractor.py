from io import BytesIO
from collections import Counter
from typing import Union, Any, Optional

from tika import parser
from nltk.corpus import stopwords
from wordfreq import tokenize
from worker.config.settings import TIKA_SERVER_ENDPOINT

language = "es"

def extract_words_from_buffer(data: bytes) -> Union[Counter[Any], tuple[Counter[str], Any]]:
    """
    Extracts and tokenizes words from any text-based file.

    Automatically detects the language using Tika's metadata,
    falling back to DEFAULT_LANGUAGE if detection fails.
    """
    parsed = parser.from_buffer(BytesIO(data), serverEndpoint=TIKA_SERVER_ENDPOINT)
    text = parsed.get("content", "")
    if not text:
        return Counter()

    # Detect language if available
    metadata = parsed.get("metadata", {})


    text = text.lower().strip()

    lang_name = "spanish" if language.startswith("es") else language
    try:
        stop_words = set(stopwords.words(lang_name))
    except LookupError:
        import nltk
        nltk.download("stopwords")
        stop_words = set(stopwords.words(lang_name))

    # Tokenize
    tokens = tokenize(text, language)
    words = [t for t in tokens if t.isalpha() and t not in stop_words]

    return Counter(words), language

