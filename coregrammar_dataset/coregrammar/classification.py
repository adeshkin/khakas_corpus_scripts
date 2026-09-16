from __future__ import annotations

import re


WORD_RE = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*", re.UNICODE)


PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "question",
        re.compile(
            r"(?:\?|\b(?:кто|что|где|куда|откуда|когда|почему|зачем|как|какой|какая|какие|сколько|ли)\b)",
            re.IGNORECASE,
        ),
    ),
    (
        "negation_prohibition",
        re.compile(r"\b(?:не|нет|нельзя|никто|ничего|никогда|никуда|без)\b", re.IGNORECASE),
    ),
    (
        "imperative_request",
        re.compile(
            r"\b(?:пожалуйста|давай(?:те)?|прошу|позволь(?:те)?|не\s+надо|не\s+нужно|"
            r"включи(?:те)?|выключи(?:те)?|покажи(?:те)?|скажи(?:те)?|позвони(?:те)?|"
            r"открой(?:те)?|закрой(?:те)?|купи(?:те)?|принеси(?:те)?|помоги(?:те)?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "possession_modality_impersonal",
        re.compile(
            r"\b(?:у\s+(?:меня|тебя|него|неё|нее|нас|вас|них)\s+(?:есть|нет)|"
            r"мне|тебе|ему|ей|нам|вам|им)\s+(?:нужно|надо|можно|нельзя|хочется)|"
            r"\b(?:можно|нельзя|следует|приходится|хочется|нужно|надо)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "motion_location",
        re.compile(
            r"\b(?:идти|пойти|ходить|ехать|поехать|ездить|прийти|приходить|приехать|"
            r"уйти|уехать|вернуться|находиться|стоять|лежать|жить|гулять|домой|"
            r"здесь|там|рядом|где|куда|откуда|из\s+города|в\s+город)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "temporal_aspectual",
        re.compile(
            r"\b(?:когда|пока|прежде\s+чем|после\s+того\s+как|как\s+только|"
            r"сначала|потом|наконец|уже|ещ[её]|начал[аио]?|продолжил[аио]?|перестал[аио]?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "relative_attributive",
        re.compile(
            r"\b(?:котор(?:ый|ая|ое|ые|ого|ой|ому|ым|ую|ых|ыми)|чей|чья|чь[её]|чьи|"
            r"тот,?\s+кто|та,?\s+которая|место,?\s+где)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "condition_cause_purpose_concession",
        re.compile(
            r"\b(?:если|чтобы|потому\s+что|так\s+как|хотя|несмотря\s+на|для\s+того\s+чтобы|иначе)\b",
            re.IGNORECASE,
        ),
    ),
)


def classify_constructions(text: str) -> tuple[str, ...]:
    labels = [label for label, pattern in PATTERNS if pattern.search(text)]
    words = WORD_RE.findall(text)
    if len(words) <= 3 and re.match(
        r"^\s*(?:да|нет|конечно|ладно|хорошо|спасибо|правда|не знаю|может быть)\b",
        text,
        re.I,
    ):
        labels.append("dialogue_ellipsis")
    if not labels:
        labels.append("simple_clause")
    return tuple(dict.fromkeys(labels))
