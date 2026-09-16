#!/usr/bin/env python3
"""Build an auditable Russian/Khakas review of the Gatitos CSV dataset."""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence


INPUT_COLUMNS = ["en", "ru_from_en_by_google", "kjh_from_ru_by_yandex"]
REVIEW_COLUMNS = [
    "ru_corrected",
    "kjh_corrected",
    "kjh_sources",
    "function_word_handling",
    "frequent_kjh",
    "native_review",
    "review_status",
    "review_flags",
    "review_note",
]
OUTPUT_COLUMNS = INPUT_COLUMNS + REVIEW_COLUMNS
VALID_STATUSES = {
    "confirmed", "grammatical", "unverified_yandex", "unverified_source", "missing",
}
VALID_FUNCTION_WORD_HANDLING = {
    "not_applicable", "lexical_equivalent", "postposition", "case_suffix", "omitted", "context_required",
}
VALID_NATIVE_REVIEW = {"none", "recommended", "required"}
VALID_FLAGS = {
    "ru_changed",
    "kjh_changed",
    "ambiguous_en",
    "multiple_kjh",
    "yandex_unverified",
    "missing_after_ru_correction",
    "missing_no_candidate",
    "function_word",
    "zero_correspondence",
    "context_dependent",
    "yandex_promoted",
    "sense_rank_over_3",
    "unverified_source",
    "frequent_kjh",
    "literary_only",
}

SOURCE_ORDER = [
    ("base", "russian-khakas-base-phrases"),
    ("explanatory", "khakas-explanatory-dict"),
    ("literary", "russian-khakas-literary-dict"),
    ("khakas_russian", "khakas-russian-dict"),
]
SOURCE_NAMES = [name for _, name in SOURCE_ORDER]

# The source list contains isolated lexemes without context. Corrections are
# deliberately conservative: only explicit review decisions are recorded here.
DEFAULT_RU_OVERRIDES = {
    "a": "неопределённый артикль",
    "the": "определённый артикль",
    "complete": "завершать",
    "who": "кто",
    "ewe": "эве",
    "how are you": "как дела",
    "true": "истина",
    "false": "ложь",
    "great": "отличный",
    "will": "будет",
    "hard": "трудный",
    "call": "звонить",
    "offer": "предлагать",
    "free": "свободный",
    "set": "устанавливать",
    "cool": "классный",
}

# Exact source matches still need semantic/grammatical filtering. These entries
# prevent dictionary case forms and unrelated homonyms from leaking into output.
KJH_SELECTIONS_BY_RU = {
    "привет": ["изен"],
    "для": ["ӱчӱн"],
    "я": ["мин"],
    "ты": ["син"],
    "мы": ["піс"],
    "вы": ["сірер"],
    "он": ["ол"],
    "она": ["ол"],
    "они": ["олар"],
    "кто": ["кем"],
    "тот": ["тігі", "ол"],
    "этот": ["пу"],
    "такой": ["андағ"],
    "человек": ["кізі"],
    "делать": ["идерге"],
    "идти": ["парарға"],
    "да": ["я"],
    "нет": ["чох"],
    "завершать": ["тоозарға", "тӱгедерге"],
    "снег": ["хар", "чаас"],
}

# Variants confirmed inside full dictionary articles but not reachable through
# exact `semgloss` matching. Each entry was reviewed against the chosen Russian
# sense and retains the source that contains the evidence.
CURATED_ARTICLE_CANDIDATES = {
    "завершать": {
        "khakas-russian-dict": ["тоозарға", "тӱгедерге"],
    },
}

CURATED_SENSE_RANKS = {
    ("привет", "изен"): 2,
}

SENSE_EQUIVALENTS_BY_RU = {
    "завершать": {"кончать", "заканчивать", "приводить к концу"},
    "отлично": {"замечательный", "очень хорошо", "здорово"},
    "великолепный": {"замечательный", "очень хороший"},
}

STRUCTURAL_FUNCTION_WORDS = {
    "a": "omitted",
    "an": "omitted",
    "the": "omitted",
    "in": "case_suffix",
    "at": "case_suffix",
    "on": "case_suffix",
    "to": "case_suffix",
    "into": "case_suffix",
    "from": "case_suffix",
    "of": "case_suffix",
    "with": "context_required",
}
PREPOSITIONS = {
    "about", "above", "across", "after", "against", "along", "among", "around",
    "before", "behind", "below", "beside", "between", "beyond", "by", "during",
    "for", "near", "over", "since", "through", "toward", "towards", "under",
    "until", "within", "without",
}
OTHER_FUNCTION_WORDS = {
    "although", "and", "because", "but", "either", "even", "however", "if",
    "neither", "no", "nor", "not", "only", "or", "so", "still", "though",
    "while", "yes", "yet",
}

AMBIGUOUS_EN = {
    "address", "advance", "aim", "air", "appeal", "arm", "back", "band",
    "bank", "bar", "base", "bear", "beat", "bill", "block", "board",
    "book", "break", "bright", "call", "case", "change", "charge", "check",
    "close", "complete", "cool", "course", "date", "direct", "draw", "drive",
    "drop", "fair", "fall", "fast", "field", "figure", "fine", "firm",
    "flat", "force", "form", "free", "great", "ground", "hand", "hard",
    "head", "hold", "interest", "kind", "last", "lead", "left", "light",
    "like", "line", "live", "long", "love", "mark", "match", "mean",
    "mind", "miss", "move", "object", "offer", "order", "park", "patient",
    "place", "plain", "plant", "point", "practice", "present", "press",
    "record", "rest", "right", "ring", "rock", "round", "run", "set",
    "show", "sign", "sound", "spot", "spring", "stand", "state", "still",
    "store", "straight", "subject", "support", "sweet", "table", "take",
    "track", "train", "trip", "turn", "view", "watch", "well", "will",
    "work", "wrap",
}


@dataclass(frozen=True)
class SourceIndexes:
    base: Mapping[str, list[str]]
    khakas_russian: Mapping[str, list[str]]
    explanatory: Mapping[str, list[str]]
    literary: Mapping[str, list[str]]
    khakas_senses: Mapping[str, list[str]] = field(default_factory=dict)


def normalize_lookup(value: str) -> str:
    """Normalize only for matching; never use this representation in output."""
    value = unicodedata.normalize("NFC", value or "").casefold().replace("ё", "е")
    value = re.sub(r"[^0-9a-zа-яӧӱңғҷі]+", " ", value, flags=re.IGNORECASE)
    return " ".join(value.split())


def _dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for raw in values:
        value = unicodedata.normalize("NFC", (raw or "").strip())
        key = normalize_lookup(value)
        if value and key and key not in seen:
            seen.add(key)
            result.append(value)
    return result


def _read_csv(path: Path, expected_header: Sequence[str]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(expected_header):
            raise ValueError(
                f"{path.name}: expected header {list(expected_header)!r}, "
                f"got {reader.fieldnames!r}"
            )
        rows = list(reader)
    for number, row in enumerate(rows, start=2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"{path.name}:{number}: malformed CSV row")
    return rows


def _add(index: dict[str, list[str]], key: str, value: str) -> None:
    normalized_key = normalize_lookup(key)
    if normalized_key and value.strip():
        index[normalized_key].append(value.strip())


def _semgloss_keys(value: str) -> list[str]:
    value = re.sub(r"\s*\([^)]*\)\s*$", "", value or "").strip()
    keys = [value]
    # A semicolon normally separates dictionary senses, while commas are often
    # true synonyms. Both are candidate keys and are filtered later.
    keys.extend(part.strip() for part in re.split(r"[;,]", value) if part.strip())
    return _dedupe(keys)


def _clean_headword(value: str) -> str:
    value = (value or "").replace("\\", "")
    value = re.sub(r"\s*\[[^]]*]\s*", " ", value or "")
    value = re.sub(r"\s+[IVX]+$", "", value.strip())
    return " ".join(value.split()).lower()


def _russian_glosses(field: str) -> list[str]:
    """Extract conservative Russian glosses that follow dictionary `--` marks."""
    field = re.sub(r"</?[biі]>", "", field or "", flags=re.IGNORECASE)
    field = field.replace("**", "").replace("*", "")
    results: list[str] = []
    for segment in re.findall(r"--\s*([^\n]+?)(?=(?:--|$))", field):
        segment = re.split(r"[.!?](?:\s|$)", segment, maxsplit=1)[0]
        segment = re.sub(r"\([^)]*\)", "", segment)
        if len(normalize_lookup(segment).split()) > 6:
            continue
        for part in re.split(r"[;,]", segment):
            part = re.sub(r"\b(?:кого|кому|кем|что|чего|чему|чем)-л\.?\b", "", part, flags=re.IGNORECASE)
            part = " ".join(part.strip(" .:-").split())
            if part and len(part.split()) <= 6:
                results.append(part)
    return _dedupe(results)


def _field_russian_senses(field: str) -> list[str]:
    """Extract short leading Russian senses from a Khakas–Russian article."""
    field = re.sub(r"^\s*<b>.*?</b>", "", field or "", count=1, flags=re.IGNORECASE)
    field = re.split(r"<b>", field, maxsplit=1, flags=re.IGNORECASE)[0]
    field = re.sub(r"</?[^>]+>", " ", field)
    field = re.sub(
        r"\b(?:сущ|прил|нареч|гл|мест|союз|межд|част)\.?\b", " ", field,
        flags=re.IGNORECASE,
    )
    field = re.sub(r"\b[IVX]+\b", " ", field)
    results: list[str] = []
    for part in re.split(r"(?:\d+\)|[;,/])", field):
        part = re.sub(r"\([^)]*\)", "", part)
        part = " ".join(part.strip(" .:-").split())
        if part and len(part.split()) <= 5:
            results.append(part)
    return _dedupe(results)


def _literary_candidate(headword: str, field: str) -> str:
    """Return only an unmistakably short Khakas equivalent at article start."""
    text = re.sub(r"^\s*\*\*.*?\*\*", "", field or "", count=1).strip()
    first = re.split(r"[.!?]", text, maxsplit=1)[0].strip(" ,-:;")
    if not first or len(first.split()) > 4 or not re.search(r"[ӧӱңғҷі]", first, re.IGNORECASE):
        return ""
    return first


def build_source_indexes(paths: Mapping[str, Path]) -> SourceIndexes:
    base_rows = _read_csv(paths["base"], ["ru", "kjh"])
    kr_rows = _read_csv(paths["khakas_russian"], ["word", "semgloss", "field1"])
    ex_rows = _read_csv(paths["explanatory"], ["headword_fix", "field_fix"])
    lit_rows = _read_csv(paths["literary"], ["headword_fix", "field_fix"])

    base: dict[str, list[str]] = defaultdict(list)
    khakas_russian: dict[str, list[str]] = defaultdict(list)
    explanatory: dict[str, list[str]] = defaultdict(list)
    literary: dict[str, list[str]] = defaultdict(list)
    khakas_senses: dict[str, list[str]] = defaultdict(list)

    for row in base_rows:
        _add(base, row["ru"], row["kjh"])
    for row in kr_rows:
        word_key = normalize_lookup(row["word"])
        article_senses = _field_russian_senses(row["field1"])
        combined_sense = "; ".join(_dedupe([row["semgloss"], *article_senses]))
        khakas_senses[word_key].append(combined_sense)
        for key in _semgloss_keys(combined_sense):
            _add(khakas_russian, key, row["word"])
    for row in ex_rows:
        headword = _clean_headword(row["headword_fix"])
        for gloss in _russian_glosses(row["field_fix"]):
            _add(explanatory, gloss, headword)

    for row in lit_rows:
        candidate = _literary_candidate(row["headword_fix"], row["field_fix"])
        if candidate:
            _add(literary, row["headword_fix"], candidate)

    return SourceIndexes(
        base={key: _dedupe(values) for key, values in base.items()},
        khakas_russian={key: _dedupe(values) for key, values in khakas_russian.items()},
        explanatory={key: _dedupe(values) for key, values in explanatory.items()},
        literary={key: _dedupe(values) for key, values in literary.items()},
        khakas_senses={key: _dedupe(values) for key, values in khakas_senses.items()},
    )


def _is_russian_infinitive(value: str) -> bool:
    word = normalize_lookup(value)
    return " " not in word and bool(re.search(r"(?:ть|ться|ти|чь)$", word))


def _is_khakas_infinitive(value: str) -> bool:
    return bool(re.search(r"р(?:ға|ге)$", normalize_lookup(value)))


def collect_candidate_details(
    russian: str, indexes: SourceIndexes
) -> tuple[list[str], list[str], dict[str, list[str]]]:
    key = normalize_lookup(russian)
    candidates: list[str] = []
    candidate_sources: dict[str, list[str]] = defaultdict(list)
    used_sources: list[str] = []

    for attribute, source_name in SOURCE_ORDER:
        source_values = list(getattr(indexes, attribute).get(key, []))
        source_values.extend(CURATED_ARTICLE_CANDIDATES.get(key, {}).get(source_name, []))
        if _is_russian_infinitive(russian):
            source_values = [value for value in source_values if _is_khakas_infinitive(value)]
        if attribute in {"explanatory", "literary"} and candidates:
            existing_keys = {normalize_lookup(value) for value in candidates}
            source_values = [
                value
                for value in source_values
                if normalize_lookup(value) in existing_keys
                or normalize_lookup(value) in indexes.khakas_senses
            ]
        if not source_values:
            continue
        accepted_in_source = False
        for value in source_values:
            candidate_key = normalize_lookup(value)
            if not candidate_key:
                continue
            existing = next((item for item in candidates if normalize_lookup(item) == candidate_key), None)
            if existing is None:
                candidates.append(value)
                existing = value
            if source_name not in candidate_sources[normalize_lookup(existing)]:
                candidate_sources[normalize_lookup(existing)].append(source_name)
            accepted_in_source = True
        if accepted_in_source:
            used_sources.append(source_name)

    selected = KJH_SELECTIONS_BY_RU.get(key)
    if selected is not None:
        allowed = {normalize_lookup(value) for value in selected}
        candidates = [value for value in candidates if normalize_lookup(value) in allowed]
        candidates.sort(key=lambda value: [normalize_lookup(v) for v in selected].index(normalize_lookup(value)))
        used_sources = []
        for _, source_name in SOURCE_ORDER:
            if any(source_name in candidate_sources[normalize_lookup(value)] for value in candidates):
                used_sources.append(source_name)

    return candidates, used_sources, dict(candidate_sources)


def candidate_sense_rank(candidate: str, russian: str, indexes: SourceIndexes) -> int | None:
    """Return the 1-based rank of the requested Russian sense for a KJH word."""
    russian_key = normalize_lookup(russian)
    curated_rank = CURATED_SENSE_RANKS.get(
        (russian_key, normalize_lookup(candidate))
    )
    if curated_rank is not None:
        return curated_rank
    wanted = {russian_key}
    wanted.update(
        normalize_lookup(value) for value in SENSE_EQUIVALENTS_BY_RU.get(russian_key, set())
    )
    for rank, sense in enumerate(
        indexes.khakas_senses.get(normalize_lookup(candidate), []), start=1
    ):
        keys = {normalize_lookup(value) for value in _semgloss_keys(sense)}
        if wanted & keys:
            return rank
    if indexes.khakas_senses.get(normalize_lookup(candidate)):
        return max(4, len(indexes.khakas_senses[normalize_lookup(candidate)]) + 1)
    if any(
        normalize_lookup(value) == normalize_lookup(candidate)
        for value in indexes.khakas_russian.get(russian_key, [])
    ):
        return 1
    return None


def _ordered_sources(
    candidate_keys: Sequence[str], candidate_sources: Mapping[str, list[str]]
) -> list[str]:
    used = {
        source
        for key in candidate_keys
        for source in candidate_sources.get(key, [])
    }
    return [source for source in SOURCE_NAMES if source in used]


def _escalate_native(current: str, requested: str) -> str:
    order = {"none": 0, "recommended": 1, "required": 2}
    return requested if order[requested] > order[current] else current


def collect_candidates(russian: str, indexes: SourceIndexes) -> tuple[list[str], list[str]]:
    candidates, sources, _ = collect_candidate_details(russian, indexes)
    return candidates, sources


def review_row(
    row: Mapping[str, str],
    indexes: SourceIndexes,
    *,
    ru_overrides: Mapping[str, str] | None = None,
) -> dict[str, str]:
    overrides = DEFAULT_RU_OVERRIDES if ru_overrides is None else ru_overrides
    english = (row["en"] or "").strip()
    original_ru = (row["ru_from_en_by_google"] or "").strip()
    original_kjh = (row["kjh_from_ru_by_yandex"] or "").strip()
    corrected_ru = overrides.get(english.casefold(), original_ru).strip()
    ru_changed = normalize_lookup(corrected_ru) != normalize_lookup(original_ru)
    flags: list[str] = []
    notes: list[str] = []
    native_review = "none"
    function_handling = "not_applicable"

    if ru_changed:
        flags.append("ru_changed")
        notes.append(f"Русский: «{original_ru}» → «{corrected_ru}».")
    if english.casefold() in AMBIGUOUS_EN:
        flags.append("ambiguous_en")
        native_review = _escalate_native(native_review, "recommended")
        notes.append("Английское слово многозначно; выбрано базовое значение.")

    structural = STRUCTURAL_FUNCTION_WORDS.get(english.casefold())
    if structural:
        flags.extend(["function_word", "zero_correspondence"])
        function_handling = structural
        if structural in {"case_suffix", "context_required"}:
            flags.append("context_dependent")
            native_review = "required"
            notes.append(
                "Отдельная лексема не выбрана: способ передачи зависит от контекста и грамматической формы."
            )
        else:
            notes.append("Артикль отдельно не выражается в хакасском языке.")
        result = {column: row[column] for column in INPUT_COLUMNS}
        result.update({
            "ru_corrected": corrected_ru,
            "kjh_corrected": "",
            "kjh_sources": "",
            "function_word_handling": function_handling,
            "frequent_kjh": "",
            "native_review": native_review,
            "review_status": "grammatical",
            "review_flags": "; ".join(_dedupe(flags)),
            "review_note": " ".join(notes),
        })
        return result

    candidates, _, candidate_sources = collect_candidate_details(corrected_ru, indexes)
    yandex_dictionary_rank = candidate_sense_rank(original_kjh, corrected_ru, indexes)
    if original_kjh and yandex_dictionary_rank is not None and (
        not ru_changed or yandex_dictionary_rank <= 3
    ):
        yandex_key = normalize_lookup(original_kjh)
        if not any(normalize_lookup(value) == yandex_key for value in candidates):
            candidates.append(original_kjh)
        candidate_sources.setdefault(yandex_key, []).append("khakas-russian-dict")
    all_candidate_sources = {
        source
        for sources_for_candidate in candidate_sources.values()
        for source in sources_for_candidate
    }
    if all_candidate_sources == {"khakas-explanatory-dict"} and len(candidates) > 1:
        yandex_key = normalize_lookup(original_kjh)
        matching_yandex = [
            value for value in candidates if normalize_lookup(value) == yandex_key
        ]
        if matching_yandex:
            candidates = matching_yandex
            candidate_sources = {yandex_key: candidate_sources[yandex_key]}

    accepted: list[str] = []
    rejected_ranked: list[tuple[str, int]] = []
    for candidate in candidates:
        candidate_key = normalize_lookup(candidate)
        rank = candidate_sense_rank(candidate, corrected_ru, indexes)
        sources_for_candidate = candidate_sources.get(candidate_key, [])
        literary_only = sources_for_candidate == ["russian-khakas-literary-dict"]
        if rank is not None and rank > 3:
            rejected_ranked.append((candidate, rank))
        elif literary_only and rank is None:
            continue
        else:
            accepted.append(candidate)
            if rank is not None and "khakas-russian-dict" not in sources_for_candidate:
                candidate_sources[candidate_key].append("khakas-russian-dict")

    yandex_key = normalize_lookup(original_kjh)
    matching_yandex = next(
        (value for value in accepted if normalize_lookup(value) == yandex_key), None
    )
    if matching_yandex:
        accepted = [matching_yandex] + [value for value in accepted if value != matching_yandex]
        if len(accepted) > 1:
            flags.append("yandex_promoted")

    if accepted:
        corrected_kjh = "; ".join(accepted)
        sources = _ordered_sources(
            [normalize_lookup(value) for value in accepted], candidate_sources
        )
        status = "confirmed"
        if len(accepted) > 1:
            flags.append("multiple_kjh")
            native_review = _escalate_native(native_review, "recommended")
            notes.append("Несколько подходящих хакасских вариантов.")
        if normalize_lookup(corrected_kjh) != normalize_lookup(original_kjh):
            flags.append("kjh_changed")
    elif rejected_ranked:
        candidate, rank = min(rejected_ranked, key=lambda item: item[1])
        corrected_kjh = candidate
        sources = _ordered_sources([normalize_lookup(candidate)], candidate_sources)
        status = "unverified_source"
        native_review = "required"
        flags.extend(["sense_rank_over_3", "unverified_source"])
        notes.append(
            f"Сохранён единственный лучший кандидат: нужное русское значение имеет ранг {rank}, ниже первых трёх."
        )
    elif english.casefold() in PREPOSITIONS | OTHER_FUNCTION_WORDS:
        corrected_kjh = ""
        sources = []
        status = "grammatical"
        function_handling = "context_required"
        native_review = "required"
        flags.extend(["function_word", "zero_correspondence", "context_dependent"])
        notes.append(
            "Отдельный эквивалент не подтверждён; перевод служебного слова зависит от контекста."
        )
    elif original_kjh and not ru_changed:
        corrected_kjh = original_kjh
        sources = ["yandex-unverified"]
        status = "unverified_yandex"
        native_review = _escalate_native(native_review, "recommended")
        flags.append("yandex_unverified")
        notes.append("Словарного подтверждения нет; сохранён перевод Yandex.")
    elif candidates:
        corrected_kjh = candidates[0]
        selected_key = normalize_lookup(candidates[0])
        sources = _ordered_sources([selected_key], candidate_sources)
        status = "unverified_source"
        native_review = "required"
        flags.append("unverified_source")
        if candidate_sources.get(selected_key) == ["russian-khakas-literary-dict"]:
            flags.append("literary_only")
            notes.append("Вариант найден только в потенциально ошибочном литературном словаре.")
        else:
            notes.append("Источник даёт кандидата, но первые три русских значения не подтверждены.")
    else:
        corrected_kjh = ""
        sources = []
        status = "missing"
        native_review = "required"
        if ru_changed and original_kjh:
            flags.append("missing_after_ru_correction")
            notes.append("Старый перевод Yandex относится к исправленному русскому значению и не перенесён.")
        else:
            flags.append("missing_no_candidate")
            notes.append("Подходящий хакасский вариант в источниках не найден.")

    if corrected_kjh and english.casefold() in PREPOSITIONS:
        function_handling = "postposition"
        flags.append("function_word")
    elif corrected_kjh and english.casefold() in OTHER_FUNCTION_WORDS:
        function_handling = "lexical_equivalent"
        flags.append("function_word")

    result = {column: row[column] for column in INPUT_COLUMNS}
    result.update(
        {
            "ru_corrected": corrected_ru,
            "kjh_corrected": corrected_kjh,
            "kjh_sources": "; ".join(sources),
            "function_word_handling": function_handling,
            "frequent_kjh": "",
            "native_review": native_review,
            "review_status": status,
            "review_flags": "; ".join(_dedupe(flags)),
            "review_note": " ".join(notes),
        }
    )
    return result


def apply_frequency_review(
    reviewed_rows: Sequence[Mapping[str, str]],
    indexes: SourceIndexes | None = None,
) -> list[dict[str, str]]:
    """Annotate KJH variants reused for at least two distinct Russian meanings."""
    rows = [dict(row) for row in reviewed_rows]
    usage: dict[str, dict[str, object]] = {}
    for row in rows:
        ru_key = normalize_lookup(row.get("ru_corrected", ""))
        for variant in _dedupe(row.get("kjh_corrected", "").split("; ")):
            key = normalize_lookup(variant)
            entry = usage.setdefault(key, {"form": variant, "rows": 0, "ru": set()})
            entry["rows"] = int(entry["rows"]) + 1
            ru_values = entry["ru"]
            assert isinstance(ru_values, set)
            ru_values.add(ru_key)
    frequent = {
        key: value for key, value in usage.items() if len(value["ru"]) >= 2
    }
    for row in rows:
        labels: list[str] = []
        for variant in _dedupe(row.get("kjh_corrected", "").split("; ")):
            entry = frequent.get(normalize_lookup(variant))
            if entry:
                labels.append(
                    f"{entry['form']} ({entry['rows']} строк / {len(entry['ru'])} RU)"
                )
        row["frequent_kjh"] = "; ".join(labels)
        if labels:
            row_flags = [
                value for value in row.get("review_flags", "").split("; ") if value
            ]
            row_flags.append("frequent_kjh")
            row["review_flags"] = "; ".join(_dedupe(row_flags))
            row["native_review"] = _escalate_native(
                row.get("native_review", "none"),
                "recommended" if row.get("review_status") == "confirmed" else "required",
            )
            note = row.get("review_note", "").strip()
            addition = "Частое хакасское соответствие перепроверено по русским значениям."
            row["review_note"] = f"{note} {addition}".strip()
    return rows


def build_reviewed_csv(
    main_path: Path,
    dictionary_paths: Mapping[str, Path],
    output_path: Path,
) -> None:
    rows = _read_csv(main_path, INPUT_COLUMNS)
    indexes = build_source_indexes(dictionary_paths)
    reviewed = apply_frequency_review(
        [review_row(row, indexes) for row in rows], indexes
    )
    errors = validate_reviewed_rows(rows, reviewed, expected_count=len(rows))
    if errors:
        raise ValueError("Review validation failed:\n" + "\n".join(errors[:20]))
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(reviewed)


def validate_reviewed_rows(
    source_rows: Sequence[Mapping[str, str]],
    reviewed_rows: Sequence[Mapping[str, str]],
    *,
    expected_count: int | None = None,
) -> list[str]:
    errors: list[str] = []
    if expected_count is not None and len(reviewed_rows) != expected_count:
        errors.append(f"expected {expected_count} reviewed rows, got {len(reviewed_rows)}")
    if len(source_rows) != len(reviewed_rows):
        errors.append(f"source/reviewed row count mismatch: {len(source_rows)} != {len(reviewed_rows)}")

    for number, (source, reviewed) in enumerate(zip(source_rows, reviewed_rows), start=2):
        for column in INPUT_COLUMNS:
            if reviewed.get(column) != source.get(column):
                errors.append(f"row {number}: source column {column!r} changed")
        if not (reviewed.get("ru_corrected") or "").strip():
            errors.append(f"row {number}: ru_corrected is empty")

        status = reviewed.get("review_status", "")
        kjh = reviewed.get("kjh_corrected", "")
        sources = reviewed.get("kjh_sources", "")
        handling = reviewed.get("function_word_handling", "")
        native = reviewed.get("native_review", "")
        if status not in VALID_STATUSES:
            errors.append(f"row {number}: invalid review_status {status!r}")
        if handling not in VALID_FUNCTION_WORD_HANDLING:
            errors.append(f"row {number}: invalid function_word_handling {handling!r}")
        if native not in VALID_NATIVE_REVIEW:
            errors.append(f"row {number}: invalid native_review {native!r}")
        if status == "confirmed" and (not kjh or not sources or "yandex-unverified" in sources):
            errors.append(f"row {number}: confirmed row lacks dictionary evidence")
        if status == "unverified_yandex":
            if sources != "yandex-unverified" or normalize_lookup(kjh) != normalize_lookup(source.get("kjh_from_ru_by_yandex", "")):
                errors.append(f"row {number}: invalid unverified Yandex fallback")
        if status == "missing" and kjh:
            errors.append(f"row {number}: missing row contains a Khakas translation")
        if status == "missing" and native != "required":
            errors.append(f"row {number}: missing row must require native review")
        if status == "grammatical":
            if kjh or handling not in {"omitted", "case_suffix", "context_required"}:
                errors.append(f"row {number}: invalid grammatical treatment")
            if handling in {"case_suffix", "context_required"} and native != "required":
                errors.append(
                    f"row {number}: context-dependent grammatical row must require native review"
                )
        if status == "unverified_source" and (
            not kjh or not sources or native != "required"
        ):
            errors.append(f"row {number}: invalid unverified source row")
        source_items = [value for value in sources.split("; ") if value]
        dictionary_items = [value for value in source_items if value in SOURCE_NAMES]
        if dictionary_items != [
            value for value in SOURCE_NAMES if value in dictionary_items
        ]:
            errors.append(f"row {number}: dictionary sources are out of order")
        if any(
            value not in SOURCE_NAMES + ["yandex-unverified"] for value in source_items
        ):
            errors.append(f"row {number}: unknown KJH source")

        if ";" in kjh and "; " not in kjh:
            errors.append(f"row {number}: Khakas variants do not use '; ' delimiter")
        variants = [value.strip() for value in kjh.split("; ") if value.strip()]
        normalized_variants = [normalize_lookup(value) for value in variants]
        if len(normalized_variants) != len(set(normalized_variants)):
            errors.append(f"row {number}: duplicate Khakas variant")

        flags = [value for value in reviewed.get("review_flags", "").split("; ") if value]
        unknown_flags = sorted(set(flags) - VALID_FLAGS)
        if unknown_flags:
            errors.append(f"row {number}: invalid review flags {unknown_flags!r}")
        if reviewed.get("frequent_kjh") and (
            "frequent_kjh" not in flags or native == "none"
        ):
            errors.append(f"row {number}: inconsistent frequent KJH review")
    return errors


def _default_paths(root: Path) -> tuple[Path, dict[str, Path], Path]:
    return (
        root / "gatitos_en_original_ru_google_kjh_yandex - 1.csv",
        {
            "base": root / "russian-khakas-base-phrases.csv",
            "khakas_russian": root / "khakas-russian-dict.csv",
            "explanatory": root / "khakas-explanatory-dict.csv",
            "literary": root / "russian-khakas-literary-dict.csv",
        },
        root / "gatitos_en_ru_kjh_reviewed.csv",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    main_path, dictionaries, output_path = _default_paths(args.root)
    build_reviewed_csv(main_path, dictionaries, output_path)
    source_rows = _read_csv(main_path, INPUT_COLUMNS)
    reviewed_rows = _read_csv(output_path, OUTPUT_COLUMNS)
    errors = validate_reviewed_rows(source_rows, reviewed_rows, expected_count=4001)
    if errors:
        raise SystemExit("Final validation failed:\n" + "\n".join(errors[:20]))
    print(output_path)


if __name__ == "__main__":
    main()
