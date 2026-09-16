from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, replace

from .classification import WORD_RE, classify_constructions
from .config import AppConfig
from .models import Candidate


URL_RE = re.compile(r"(?:https?://|www\.|\b\S+@\S+\.\S+)", re.IGNORECASE)
MARKUP_RE = re.compile(r"<[^>]+>|\{\{[^}]+\}\}|\[\[[^]]+\]\]")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
SPACE_RE = re.compile(r"\s+")
TERMINAL_PUNCT_RE = re.compile(r"[.!?…]+$")
PUNCT_RE = re.compile(r"[^\w\s-]", re.UNICODE)
REPEATED_RE = re.compile(r"([^\W\d_])\1{4,}", re.IGNORECASE)
LIST_RE = re.compile(r"^\s*(?:[-*•‣]|\d{1,3}[.)])\s+")
COMMON_VOICE_REGISTER_RE = re.compile(
    r"\b(?:уважаем(?:ый|ая|ые)|господин\s+председатель|товарищи|"
    r"пленарное\s+заседание|федеральн(?:ый|ого)\s+закон|настоящая\s+статья)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class FilterResult:
    candidate: Candidate
    rejection_reason: str | None = None


def normalize_display(text: str) -> str:
    return SPACE_RE.sub(" ", unicodedata.normalize("NFC", text).replace("\ufeff", " ")).strip()


def dedupe_key(text: str) -> str:
    value = normalize_display(text).lower().replace("ё", "е")
    value = TERMINAL_PUNCT_RE.sub("", value)
    value = PUNCT_RE.sub(" ", value)
    return SPACE_RE.sub(" ", value).strip()


def _cyrillic_ratio(text: str) -> float:
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return 0.0
    cyrillic = sum("CYRILLIC" in unicodedata.name(char, "") for char in letters)
    return cyrillic / len(letters)


def evaluate_candidate(candidate: Candidate, config: AppConfig) -> FilterResult:
    if "\n" in candidate.ru or "\r" in candidate.ru:
        return FilterResult(replace(candidate, ru=normalize_display(candidate.ru)), "line_break")
    if LIST_RE.search(candidate.ru):
        return FilterResult(replace(candidate, ru=normalize_display(candidate.ru)), "list_item")
    text = normalize_display(candidate.ru)
    updated = replace(candidate, ru=text)
    if URL_RE.search(text):
        return FilterResult(updated, "url")
    if MARKUP_RE.search(text):
        return FilterResult(updated, "markup")
    if CONTROL_RE.search(text):
        return FilterResult(updated, "control_character")
    if _cyrillic_ratio(text) < config.cyrillic_ratio:
        return FilterResult(updated, "not_russian")
    lowered = text.casefold().replace("ё", "е")
    if any(term.casefold().replace("ё", "е") in lowered for term in config.blocked_terms):
        return FilterResult(updated, "blocked_register")
    if candidate.source == "common_voice" and COMMON_VOICE_REGISTER_RE.search(text):
        return FilterResult(updated, "blocked_register")
    if REPEATED_RE.search(text):
        return FilterResult(updated, "probable_typo")

    labels = classify_constructions(text)
    token_count = len(WORD_RE.findall(text))
    minimum = config.dialogue_min_tokens if "dialogue_ellipsis" in labels else config.min_tokens
    if token_count < minimum:
        return FilterResult(updated, "too_short")
    if token_count > config.max_tokens:
        return FilterResult(updated, "too_long")
    digits = sum(char.isdigit() for char in text)
    if digits > 4 or (digits and digits / max(len(text), 1) > 0.15):
        return FilterResult(updated, "too_many_digits")
    if len(re.findall(r"\b[А-ЯЁ][а-яё]+\b", text[1:])) > max(3, token_count // 3):
        return FilterResult(updated, "too_many_names")

    quality = candidate.quality_score + 1.0 - abs(token_count - 9) / 30.0
    if text.endswith((".", "?", "!", "…")):
        quality += 0.05
    if candidate.source == "massive":
        quality += 0.05
    return FilterResult(replace(updated, construction_labels=labels, quality_score=quality))
