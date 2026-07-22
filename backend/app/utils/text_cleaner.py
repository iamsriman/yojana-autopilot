"""Text normalization and scoring utilities."""

import re
from collections.abc import Iterable
from difflib import SequenceMatcher


_TOKEN_RE = re.compile(r"[\w]+", re.UNICODE)

SYNONYMS: dict[str, tuple[str, ...]] = {
    "income": ("income", "aadaya", "ఆదాయ", "aadayam"),
    "certificate": ("certificate", "cert", "సర్టిఫికేట్", "patram"),
    "aadhaar": ("aadhaar", "aadhar", "uidai", "ఆధార్"),
    "ration": ("ration", "rice", "బియ్యం", "రేషన్"),
    "farmer": ("farmer", "kisan", "rythu", "raitu", "రైతు"),
    "scholarship": ("scholarship", "vidya", "deevena", "విద్య", "స్కాలర్షిప్"),
    "pension": ("pension", "bharosa", "పెన్షన్"),
    "driving": ("driving", "dl", "llr", "licence", "license"),
    "passport": ("passport", "psk", "పాస్పోర్ట్"),
}


def normalize_text(value: object) -> str:
    """Convert arbitrary JSON-ish values into compact text."""

    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    if isinstance(value, dict):
        return " ".join(normalize_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(normalize_text(v) for v in value)
    return str(value)


def tokenize(value: object) -> set[str]:
    """Return lowercase search tokens."""

    raw_tokens = {token.lower() for token in _TOKEN_RE.findall(normalize_text(value))}
    expanded = set(raw_tokens)
    for canonical, aliases in SYNONYMS.items():
        if canonical in raw_tokens or any(alias.lower() in raw_tokens for alias in aliases):
            expanded.add(canonical)
            expanded.update(alias.lower() for alias in aliases)
    return expanded


def keyword_score(query_terms: Iterable[str], haystack: object) -> float:
    """Lexical and fuzzy score used as a fallback beside vector search."""

    terms = {term.lower() for term in query_terms if term}
    if not terms:
        return 0.0
    tokens = tokenize(haystack)
    if not tokens:
        return 0.0
    exact = len(terms & tokens) / len(terms)
    fuzzy_hits = 0
    for term in terms - tokens:
        if any(SequenceMatcher(None, term, token).ratio() >= 0.82 for token in tokens):
            fuzzy_hits += 1
    fuzzy = fuzzy_hits / len(terms)
    return min(1.0, exact + (0.65 * fuzzy))
