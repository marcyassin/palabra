"""
Spanish lemmatization test using spaCy with refined cleaning logic.
This version fixes cases like 'trabajabas' → 'trabajar' and
'dormiré' / 'ibas' → 'ir' correctly.
"""

import re
import spacy

# --- Load spaCy model ---
print("🧠 Loading spaCy model for 'es'...")
try:
    nlp = spacy.load("es_core_news_lg")
except OSError:
    print("⚠️ 'es_core_news_lg' not found. Run: python -m spacy download es_core_news_lg")
    nlp = spacy.load("es_core_news_sm")

IRREGULAR_FIXES = {
    # core irregular stems
    "har": "hacer", "haga": "hacer", "hecho": "hacer",
    "habier": "haber", "habr": "haber",
    "podr": "poder", "pued": "poder", "pud": "poder",
    "querr": "querer", "quier": "querer", "quis": "querer",
    "sabr": "saber", "sup": "saber",
    "ser": "ser", "soy": "ser", "sea": "ser", "fue": "ser", "fui": "ser", "fueron": "ser",
    "ir": "ir", "iba": "ir", "ido": "ir",
    "ven": "venir", "veng": "venir", "vin": "venir", "vendr": "venir",
    "tendr": "tener", "tuv": "tener", "tien": "tener", "tengo": "tener",
    "dir": "decir", "dij": "decir", "dec": "decir", "dig": "decir",
    "valdr": "valer", "saldr": "salir",
    "traig": "traer", "traj": "traer",
    "pong": "poner", "pus": "poner", "pondr": "poner",
    "reir": "reír", "rei": "reír",
}


# --- Lemma cleanup rules ---
def clean_lemma(word: str, lemma: str) -> str:
    word_lower = word.lower()
    lemma_lower = lemma.lower()

    # 1️⃣ Fix spurious accent (hablár → hablar)
    if lemma_lower.endswith("ár"):
        lemma_lower = lemma_lower.replace("á", "a")

    # 2️⃣ Normalize accented infinitives (ír → ir)
    if lemma_lower == "ír":
        lemma_lower = "ir"

    # 3️⃣ Map 'fui', 'fue', etc. to 'ser'
    if word_lower in {"fui", "fue", "fueron", "fuiste", "fuimos"}:
        return "ser"

    # 4️⃣ Fix imperfect AR verbs (trabajabas, hablábamos → trabajar)
    if re.search(r"(aba|abas|aban|ábamos)$", word_lower) and lemma_lower == word_lower:
        return re.sub(r"(aba|abas|aban|ábamos)$", "ar", word_lower)

    # 5️⃣ Fix imperfect ER/IR verbs (comía, vivías, dormían → comer/vivir/dormir)
    if re.search(r"(ía|ías|ían|íamos)$", word_lower) and lemma_lower == word_lower:
        stem = word_lower[:-2]
        if re.search(r"(viv|dorm|sal|sub|abr|recib|decid|sent|escrib|permit|exist|part|sufr)$", stem):
            return stem + "ir"
        return stem + "er"

    # 6️⃣ Fix “ibas”, “íbamos”, “iban” → ir
    if re.search(r"^ib(a|as|an|amos|ais|as)$", word_lower):
        return "ir"

    # 7️⃣ Fix future tense mislemmatized forms like “dormiré” → dormir
    if word_lower.endswith(("ré", "rás", "rán", "remos")) and lemma_lower.startswith(word_lower[:-2]):
        if word_lower[:-2].endswith(("ar", "er", "ir")):
            return word_lower[:-2]
        return re.sub(r"(ré|rás|rán|remos)$", "r", word_lower)

    # 8️⃣ Apply irregular corrections
    normalized = lemma_lower.replace("á", "a").replace("í", "i").replace("é", "e")
    if normalized in IRREGULAR_FIXES:
        return IRREGULAR_FIXES[normalized]

    # 9️⃣ Catch malformed hybrids like hablacer, trabajacer → hablar/trabajar
    if re.search(r"(acer|ecer)$", normalized) and normalized[:-4] in {"habl", "trabaj", "est"}:
        return normalized[:-4] + "ar"

    return normalized


# --- Test words ---
test_words = [
    "trabajar","comer","vivir","amar","pensar","tener","hacer","decir","ir","venir","poder","poner",
    "querer","saber","ver","dar","salir","llegar","tomar","llevar","dejar","encontrar","seguir",
    "hablar","entender","conocer","sentir","volver","creer","parecer","quedar","pasar","esperar",
    "recordar","morir","nacer","abrir","cerrar","leer","escribir","caminar","correr","jugar","dormir",
    "reír","llorar","cantar","bailar","mirar","buscar","comprar","vender","usar","trabajando",
    "viviendo","comiendo","durmiendo","leyendo","escribiendo","jugando","riendo","bailando",
    "cantando","hablando","viendo","pensando","andando","corriendo","aprendiendo","enseñando",
    "caminando","sintiendo","trabajaba","comía","vivía","iba","decía","hacía","veía","podía",
    "quería","sabía","tenía","daba","traía","venía","salía","llegaba","tomaba","esperaba","dejaba",
    "encontraba","pensaba","amaba","abría","cerraba","lloraba","cantaba","bailaba","jugaba","corría",
    "reía","nacía","moría","viviremos","trabajaremos","hablaremos","iremos","comeremos","veremos",
    "tendremos","sabremos","podremos","haremos","diré","haré","saldré","vendré","querré","sabré",
    "podré","tendré","pondré","valdré","hablaré","viviré","trabajaré","llegaré","correré","caminaré",
    "compraré","usaré","miraré","abriré","leeré","escribiré","iré","veré","seré","estaré","harán",
    "dirán","tendrán","sabrán","podrán","vendrán","saldrán","querrán","hablarán","vivirán",
    "trabajarán","llegarán","correrán","caminarán","abrirán","leerán","escribirán","haríamos",
    "diríamos","tendríamos","sabríamos","podríamos","querríamos","saldríamos","vendríamos",
    "hablaríamos","viviríamos","trabajaríamos","llegaríamos","veríamos","comeríamos","leeríamos",
    "abriríamos","jugaríamos","dormiríamos","sería","serías","serían","seremos","soy","eres","es",
    "somos","son","fui","fuiste","fue","fuimos","fueron","era","eras","éramos","eran","he","has","ha",
    "hemos","han","había","habías","habían","hubo","hubieron","habrá","habrán","habría","habrías",
    "habrían","estoy","estás","está","estamos","están","estaba","estabas","estábamos","estaban",
    "estaré","estarán","estaríamos","tenía","tenías","tenían","tuve","tuviste","tuvo","tuvimos",
    "tuvieron","tendrás","tendrán","tendré","tendremos","puedo","puedes","puede","podemos",
    "pueden","pude","pudiste","pudo","pudimos","pudieron","podré","podrás","podrán","quiero",
    "quieres","quiere","queremos","quieren","quise","quisiste","quiso","quisimos","quisieron",
    "querré","querrás","querrán","sé","sabes","sabemos","saben","supe","supiste","supo","supimos",
    "supieron","sabré","sabrá","sabremos","voy","vas","va","vamos","van","iba","ibas","íbamos","iban",
    "iré","irás","irán","vine","viniste","vino","vinimos","vinieron","vendré","vendrás","vendrán",
    "vengo","vienes","viene","venimos","vienen","hago","haces","hace","hacemos","hacen","hice",
    "hiciste","hizo","hicimos","hicieron","haré","harás","harán","digo","dices","dice","decimos",
    "dicen","dije","dijiste","dijo","dijimos","dijeron","diré","dirás","dirán","veo","ves","ve","vemos",
    "ven","vi","viste","vio","vimos","vieron","veré","verás","verán","doy","das","da","damos","dan",
    "di","diste","dio","dimos","dieron","daré","darás","darán","salgo","sales","sale","salimos",
    "salen","salí","saliste","salió","salieron","saldré","saldrás","saldrán","duermo","duermes",
    "duerme","dormimos","duermen","dormí","dormiste","durmió","durmieron","dormiré","dormirás",
    "dormirán","camino","caminas","camina","caminamos","caminan","corrí","corriste","corrió",
    "corrimos","corrieron","corro","corres","corre","corremos","corren","corresponde","responde",
    "entiende","aprende","enseña","piensa","siente","recuerda","olvida","recibió","entregó","ganó",
    "perdió","empezó","terminó","abrió","cerró","compró","vendió","miró","buscó","encontró","llamó",
    "usó","amó","odiaba","gustaba","importaba","parecía","necesitaba","creía","sabía","pensaba",
    "decidió","intentó","logró","viajar","vivir","luchar","crecer","descansar","estudiar","enseñar",
    "aprender","jugar","dormir","beber","comer","caminar","hablar","leer","escribir","mirar","correr",
    "pensar","reír","llorar","soñar","trabajar","viajando","riendo","jugando","durmiendo","leyendo",
    "aprendiendo","enseñando","cantando","bailando","mirando","comiendo","corriendo","hablando",
    "feliz","triste","grande","pequeño","bonito","feo","rápido","lento","fuerte","débil","nuevo","viejo",
    "bueno","malo","difícil","fácil","caro","barato","importante","posible","imposible","real",
    "interesante","hermoso","maravilloso","perfecto","simple","difícilmente","fácilmente",
    "rápidamente","lentamente","probablemente","seguramente","siempre","nunca","a veces","ayer",
    "hoy","mañana","pronto","tarde","temprano","lejos","cerca","arriba","abajo","aquí","allí",
    "adentro","afuera","si","no","también","tampoco","solo","juntos","ahora","entonces","después",
    "antes","mientras","cuando","porque","aunque","pero","sin","con","sobre","entre","hacia","desde",
    "hasta","bajo","según","contra","para","por"
]


# --- Run test ---
print(f"\n{'Word':15s} {'POS':8s} {'Raw Lemma':15s} {'→ Cleaned Lemma'}")
print("-" * 65)
for w in test_words:
    doc = nlp(w)
    tok = doc[0]
    clean = clean_lemma(tok.text, tok.lemma_)
    print(f"{tok.text:15s} {tok.pos_:8s} {tok.lemma_:15s} {clean}")
