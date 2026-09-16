from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable, Mapping

from .config import allocate_counts
from .models import Candidate, SelectedRecord


class QuotaError(RuntimeError):
    """Raised when strict source or construction quotas cannot be satisfied."""


@dataclass(frozen=True, slots=True)
class SelectionResult:
    records: tuple[SelectedRecord, ...]
    requested_sources: dict[str, int]
    actual_sources: dict[str, int]
    requested_constructions: dict[str, int]
    actual_constructions: dict[str, int]
    shortages: tuple[dict[str, int | str], ...]


def _stable_rank(candidate: Candidate, seed: int) -> tuple[float, str]:
    digest = hashlib.blake2b(
        f"{seed}\0{candidate.source}\0{candidate.source_id}\0{candidate.ru}".encode("utf-8"),
        digest_size=16,
    ).hexdigest()
    return (-candidate.quality_score, digest)


def select_candidates(
    candidates: Iterable[Candidate],
    total: int,
    source_percentages: Mapping[str, float],
    construction_percentages: Mapping[str, float],
    seed: int,
    strict: bool = False,
) -> SelectionResult:
    requested_sources = allocate_counts(total, source_percentages)
    requested_constructions = allocate_counts(total, construction_percentages)
    ordered = sorted(candidates, key=lambda item: _stable_rank(item, seed))
    buckets: dict[tuple[str, str], list[Candidate]] = defaultdict(list)
    by_source: dict[str, list[Candidate]] = defaultdict(list)
    for candidate in ordered:
        by_source[candidate.source].append(candidate)
        for label in candidate.construction_labels or ("simple_clause",):
            if label in requested_constructions:
                buckets[(candidate.source, label)].append(candidate)

    positions: Counter[tuple[str, str]] = Counter()
    source_positions: Counter[str] = Counter()
    used: set[str] = set()
    actual_sources = Counter({name: 0 for name in requested_sources})
    actual_constructions = Counter({name: 0 for name in requested_constructions})
    records: list[SelectedRecord] = []

    def pop_bucket(source: str, label: str) -> Candidate | None:
        key = (source, label)
        rows = buckets[key]
        position = positions[key]
        while position < len(rows) and rows[position].key in used:
            position += 1
        positions[key] = position + 1
        return rows[position] if position < len(rows) else None

    def bucket_available(source: str, label: str) -> bool:
        key = (source, label)
        rows = buckets[key]
        position = positions[key]
        while position < len(rows) and rows[position].key in used:
            position += 1
        positions[key] = position
        return position < len(rows)

    category_order = sorted(
        requested_constructions,
        key=lambda label: (
            sum(len(buckets[(source, label)]) for source in requested_sources)
            / max(requested_constructions[label], 1),
            label,
        ),
    )
    for label in category_order:
        while actual_constructions[label] < requested_constructions[label]:
            possible_sources = [
                source
                for source in requested_sources
                if actual_sources[source] < requested_sources[source] and bucket_available(source, label)
            ]
            if not possible_sources:
                break
            source = max(
                possible_sources,
                key=lambda item: (requested_sources[item] - actual_sources[item], item == "tatoeba", item),
            )
            candidate = pop_bucket(source, label)
            if candidate is None:
                continue
            used.add(candidate.key)
            actual_sources[source] += 1
            actual_constructions[label] += 1
            records.append(SelectedRecord(candidate, label))

    def pop_source(source: str) -> Candidate | None:
        rows = by_source[source]
        position = source_positions[source]
        while position < len(rows) and rows[position].key in used:
            position += 1
        source_positions[source] = position + 1
        return rows[position] if position < len(rows) else None

    # Fill remaining source quotas even when an exact construction intersection is absent.
    for source, target in requested_sources.items():
        while len(records) < total and actual_sources[source] < target:
            candidate = pop_source(source)
            if candidate is None:
                break
            labels = [x for x in candidate.construction_labels if x in requested_constructions]
            primary = max(
                labels or ["simple_clause"],
                key=lambda label: requested_constructions.get(label, 0) - actual_constructions.get(label, 0),
            )
            used.add(candidate.key)
            actual_sources[source] += 1
            actual_constructions[primary] += 1
            records.append(SelectedRecord(candidate, primary))

    # Non-strict redistribution: Tatoeba first, then Common Voice, then MASSIVE.
    if not strict and len(records) < total:
        priority = ["tatoeba", "common_voice", "massive"]
        priority.extend(name for name in requested_sources if name not in priority)
        made_progress = True
        while len(records) < total and made_progress:
            made_progress = False
            for source in priority:
                candidate = pop_source(source)
                if candidate is None:
                    continue
                labels = [x for x in candidate.construction_labels if x in requested_constructions]
                primary = max(
                    labels or ["simple_clause"],
                    key=lambda label: requested_constructions.get(label, 0) - actual_constructions.get(label, 0),
                )
                used.add(candidate.key)
                actual_sources[source] += 1
                actual_constructions[primary] += 1
                records.append(SelectedRecord(candidate, primary))
                made_progress = True
                if len(records) == total:
                    break

    shortages: list[dict[str, int | str]] = []
    for name, target in requested_sources.items():
        if actual_sources[name] != target:
            shortages.append(
                {"dimension": "source", "name": name, "requested": target, "actual": actual_sources[name]}
            )
    for name, target in requested_constructions.items():
        if actual_constructions[name] != target:
            shortages.append(
                {
                    "dimension": "construction",
                    "name": name,
                    "requested": target,
                    "actual": actual_constructions[name],
                }
            )
    if len(records) < total:
        shortages.append(
            {"dimension": "total", "name": "total", "requested": total, "actual": len(records)}
        )
    if strict and shortages:
        summary = ", ".join(
            f"{item['dimension']} {item['name']}: {item['actual']}/{item['requested']}" for item in shortages
        )
        raise QuotaError(f"unfillable quotas: {summary}")
    if len(records) < total:
        raise QuotaError(f"insufficient candidate pool: {len(records)}/{total}")

    records.sort(key=lambda row: _stable_rank(row.candidate, seed))
    return SelectionResult(
        records=tuple(records),
        requested_sources=dict(requested_sources),
        actual_sources={name: actual_sources[name] for name in requested_sources},
        requested_constructions=dict(requested_constructions),
        actual_constructions={name: actual_constructions[name] for name in requested_constructions},
        shortages=tuple(shortages),
    )

