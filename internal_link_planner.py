import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk, RegexpParser

# Download required NLTK data (first run only)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')


# =====================================================
# CONFIG — SEO SAFE DEFAULTS (GENERAL WEBSITES)
# =====================================================

UTILITY_KEYWORDS = [
    "privacy",
    "terms",
    "cookie",
    "disclaimer",
    "contact",
    "login",
    "signup"
]

STOPWORDS = {
    "the", "and", "to", "of", "that", "is", "with", "for", "in",
    "on", "by", "as", "at", "from", "this", "it", "are", "be"
}

MIN_PILLAR_WORDS = 300        # FIX #1: softened for small/medium sites
MIN_ANCHOR_WORDS = 2
MAX_ANCHOR_WORDS = 5


# =====================================================
# HELPERS
# =====================================================

def is_utility_page(url: str) -> bool:
    url = url.lower()
    return any(k in url for k in UTILITY_KEYWORDS)


# ---------------------------
# FIX #2: SMART PILLAR LOGIC
# ---------------------------

def identify_pillar(cluster_pages):
    """
    Pillar = most comprehensive non-utility page
    RELATIVE to the cluster (not a hard global rule).
    """

    valid = [
        p for p in cluster_pages
        if not is_utility_page(p["url"])
        and len(p["content"].split()) >= MIN_PILLAR_WORDS
    ]

    # Fallback: longest non-utility page in cluster
    if not valid:
        valid = [
            p for p in cluster_pages
            if not is_utility_page(p["url"])
        ]

    if not valid:
        return None

    return max(valid, key=lambda p: len(p["content"]))


def extract_candidate_phrases(sentence: str):
    """
    Extract noun phrases (2–5 words) from visible text using POS tagging.
    Grammar: Adjective(s) + Noun(s) only.
    More natural and semantically sound than regex-based extraction.
    """
    try:
        tokens = word_tokenize(sentence.lower())
        pos_tags = pos_tag(tokens)
        
        # Define noun phrase grammar: optional adjectives + required nouns
        grammar = r"""
        NP: {<JJ>*<NN.*>+}
        """
        parser = RegexpParser(grammar)
        tree = parser.parse(pos_tags)
        
        phrases = []
        for subtree in tree.subtrees(filter=lambda t: t.label() == 'NP'):
            phrase = " ".join([word for word, _ in subtree.leaves()])
            # Only keep 2–5 word phrases
            word_count = len(phrase.split())
            if MIN_ANCHOR_WORDS <= word_count <= MAX_ANCHOR_WORDS:
                phrases.append(phrase)
        
        return phrases if phrases else []
    
    except Exception:
        # Fallback to simple regex if POS tagging fails
        words = re.findall(r"\b[a-zA-Z]{3,}\b", sentence.lower())
        phrases = []
        for i in range(len(words)):
            for j in range(i + MIN_ANCHOR_WORDS, min(i + MAX_ANCHOR_WORDS + 1, len(words))):
                phrase = " ".join(words[i:j])
                phrases.append(phrase)
        return phrases



def clean_anchor(anchor: str):
    """
    Remove stopwords and enforce anchor length rules.
    """
    words = [w for w in anchor.split() if w not in STOPWORDS]

    if MIN_ANCHOR_WORDS <= len(words) <= MAX_ANCHOR_WORDS:
        return " ".join(words)

    return None


def score_phrase(phrase: str, target_content: str) -> int:
    """
    Score phrase by semantic overlap with target page content.
    """
    phrase_words = phrase.split()
    target_words = set(target_content.lower().split())
    return sum(1 for w in phrase_words if w in target_words)


def select_best_anchor(sentence: str, target_content: str):
    """
    Primary semantic anchor selection.
    Validates anchor relevance to target page content.
    """
    phrases = extract_candidate_phrases(sentence)
    scored = []

    for p in phrases:
        score = score_phrase(p, target_content)
        # Only consider phrases with meaningful overlap (2+ words match)
        if score >= 2:
            scored.append((p, score))

    if not scored:
        return None

    scored.sort(key=lambda x: (x[1], len(x[0])), reverse=True)
    best_phrase = scored[0][0]
    
    # Final safety check: anchor must be at least 2 words of semantic value
    cleaned = clean_anchor(best_phrase)
    if cleaned and len(cleaned.split()) >= 2:
        return cleaned
    
    return None


# ---------------------------
# FIX #3: SAFE FALLBACK LOGIC
# ---------------------------

def fallback_anchor(sentence: str):
    """
    Last-resort anchor:
    first clean noun-like phrase already visible on the page.
    Still Google-safe.
    """
    phrases = extract_candidate_phrases(sentence)
    for p in phrases:
        cleaned = clean_anchor(p)
        if cleaned:
            return cleaned
    return None


# =====================================================
# CORE SEMANTIC LINK PLANNER
# =====================================================

def plan_semantic_links(clusters):
    links = []

    for cluster_pages in clusters.values():
        if len(cluster_pages) < 2:
            continue

        pillar = identify_pillar(cluster_pages)
        if not pillar:
            continue

        for page in cluster_pages:
            if page["url"] == pillar["url"]:
                continue

            if is_utility_page(page["url"]):
                continue

            sentences = re.split(r'(?<=[.!?])\s+', page["content"])

            for sentence in sentences:
                anchor = select_best_anchor(sentence, pillar["content"])

                if not anchor:
                    anchor = fallback_anchor(sentence)

                if anchor:
                    links.append({
                        "from": page["url"],
                        "to": pillar["url"],
                        "anchor": anchor,
                        "sentence": sentence.strip()
                    })
                    break  # ONE link per page (Google-safe)

    return links
