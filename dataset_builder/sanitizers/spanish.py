"""
Spanish lemma sanitizer for spaCy lemmatization output.
Fixes common irregulars, imperfects, future/conditional truncations,
and malformed stems produced by default spaCy models.
"""

import re

IRREGULAR_FIXES = {
    "har": "hacer", "haga": "hacer", "hecho": "hacer",
    "habier": "haber", "habr": "haber",
    "podr": "poder", "pued": "poder", "pud": "poder",
    "querr": "querer", "quier": "querer", "quis": "querer",
    "sabr": "saber", "sup": "saber",
    "ser": "ser", "soy": "ser", "sea": "ser",
    "fue": "ser", "fui": "ser", "fueron": "ser",
    "ir": "ir", "iba": "ir", "ido": "ir",
    "ven": "venir", "veng": "venir", "vin": "venir", "vendr": "venir",
    "tendr": "tener", "tuv": "tener", "tien": "tener", "tengo": "tener",
    "dir": "decir", "dij": "decir", "dec": "decir", "dig": "decir",
    "valdr": "valer", "saldr": "salir",
    "traig": "traer", "traj": "traer",
    "pong": "poner", "pus": "poner", "pondr": "poner",
    "reir": "reír", "rei": "reír",
}


def clean_lemma(word: str, lemma: str) -> str:
    """Return a normalized lemma for a Spanish token."""
    word_lower = word.lower()
    lemma_lower = lemma.lower()

    # Fix accidental accented infinitives (hablár → hablar)
    if lemma_lower.endswith("ár"):
        lemma_lower = lemma_lower.replace("á", "a")

    # Normalize accented infinitives (ír → ir)
    if lemma_lower == "ír":
        lemma_lower = "ir"

    # 'fui', 'fue', etc. → ser
    if word_lower in {"fui", "fue", "fueron", "fuiste", "fuimos"}:
        return "ser"

    # Imperfect -ar verbs
    if re.search(r"(aba|abas|aban|ábamos)$", word_lower) and lemma_lower == word_lower:
        return re.sub(r"(aba|abas|aban|ábamos)$", "ar", word_lower)

    # Imperfect -er/-ir verbs
    if re.search(r"(ía|ías|ían|íamos)$", word_lower) and lemma_lower == word_lower:
        stem = word_lower[:-2]
        if re.search(r"(viv|dorm|sal|sub|abr|recib|decid|sent|escrib|permit|exist|part|sufr)$", stem):
            return stem + "ir"
        return stem + "er"

    # 'ibas', 'íbamos', etc. → ir
    if re.search(r"^ib(a|as|an|amos|ais|as)$", word_lower):
        return "ir"

    # Future tense mislemmatized forms like “dormiré” → dormir
    if word_lower.endswith(("ré", "rás", "rán", "remos")) and lemma_lower.startswith(word_lower[:-2]):
        if word_lower[:-2].endswith(("ar", "er", "ir")):
            return word_lower[:-2]
        return re.sub(r"(ré|rás|rán|remos)$", "r", word_lower)

    # Irregular fixes
    normalized = lemma_lower.replace("á", "a").replace("í", "i").replace("é", "e")
    if normalized in IRREGULAR_FIXES:
        return IRREGULAR_FIXES[normalized]

    # Catch malformed hybrids like hablacer, trabajacer
    if re.search(r"(acer|ecer)$", normalized) and normalized[:-4] in {"habl", "trabaj", "est"}:
        return normalized[:-4] + "ar"

    return normalized
