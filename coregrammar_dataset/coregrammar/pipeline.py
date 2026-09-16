from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .config import AppConfig, allocate_counts
from .filtering import dedupe_key, evaluate_candidate
from .models import Candidate, SelectedRecord
from .output import write_outputs
from .selection import QuotaError, SelectionResult, select_candidates
from .sources import iter_jsonl_candidates, load_source, write_jsonl_candidates


def _fingerprint(source: str, config: AppConfig) -> str:
    payload = {
        "version": 2,
        "source": source,
        "source_config": asdict(config.sources[source]),
        "filters": {
            "min_tokens": config.min_tokens,
            "max_tokens": config.max_tokens,
            "dialogue_min_tokens": config.dialogue_min_tokens,
            "cyrillic_ratio": config.cyrillic_ratio,
            "blocked_terms": config.blocked_terms,
        },
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def _near_signature(text: str) -> str:
    tokens = dedupe_key(text).split()
    return " ".join(sorted(tokens)) if len(tokens) >= 4 else ""


def _load_blocklist(config: AppConfig, offline: bool) -> tuple[set[str], list[str]]:
    blocked: set[str] = set()
    failures: list[str] = []
    for spec in config.blocklist_datasets:
        label = str(spec.get("dataset") or spec.get("local_path") or "unknown")
        try:
            if spec.get("local_path"):
                path = Path(str(spec["local_path"])).expanduser()
                with path.open(encoding="utf-8") as handle:
                    rows: Iterable[dict[str, Any]] = (json.loads(line) for line in handle if line.strip())
            else:
                from datasets import DownloadConfig, load_dataset

                rows = load_dataset(
                    str(spec["dataset"]),
                    spec.get("config"),
                    split=str(spec.get("split", "train")),
                    streaming=True,
                    revision=spec.get("revision"),
                    download_config=DownloadConfig(local_files_only=offline),
                )
            fields = tuple(spec.get("fields", ("ru",)))
            found = 0
            for row in rows:
                for field in fields:
                    value = row.get(field)
                    if isinstance(value, str) and value.strip():
                        blocked.add(dedupe_key(value))
                        found += 1
            if found == 0:
                raise ValueError(f"none of the configured text fields were found: {fields}")
        except Exception as exc:  # optional/gated collections are reported in the manifest
            failures.append(f"{label}: {type(exc).__name__}: {exc}")
    return blocked, failures


def _build_or_load_cache(
    source: str,
    config: AppConfig,
    cache_dir: Path,
    offline: bool,
) -> tuple[list[Candidate], list[dict[str, str]]]:
    fingerprint = _fingerprint(source, config)
    clean_path = cache_dir / "clean" / f"{source}-{fingerprint}.jsonl"
    rejected_path = cache_dir / "clean" / f"{source}-{fingerprint}.rejected.jsonl"
    if clean_path.exists():
        rejected = []
        if rejected_path.exists():
            rejected = [json.loads(line) for line in rejected_path.read_text(encoding="utf-8").splitlines()]
        return list(iter_jsonl_candidates(clean_path)), rejected

    # Build once for every allowed --total so subsequent runs reuse the cleaned pool.
    maximum_main = allocate_counts(100_000, config.source_percentages)[source]
    cap = math.ceil(maximum_main * (1 + config.reserve_percentage / 100) * config.oversample_factor)
    accepted: list[Candidate] = []
    rejected: list[dict[str, str]] = []
    seen: set[str] = set()
    for candidate in load_source(source, config.sources[source], cache_dir, offline):
        result = evaluate_candidate(candidate, config)
        if result.rejection_reason:
            if len(rejected) < config.max_rejected_rows:
                rejected.append({
                    "ru": result.candidate.ru, "source": source,
                    "source_id": result.candidate.source_id, "reason": result.rejection_reason,
                })
            continue
        key = dedupe_key(result.candidate.ru)
        if not key or key in seen:
            if len(rejected) < config.max_rejected_rows:
                rejected.append({
                    "ru": result.candidate.ru, "source": source,
                    "source_id": result.candidate.source_id, "reason": "duplicate_within_source",
                })
            continue
        seen.add(key)
        accepted.append(result.candidate)
        if len(accepted) >= cap:
            break
    write_jsonl_candidates(clean_path, accepted)
    rejected_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = rejected_path.with_suffix(rejected_path.suffix + ".part")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rejected:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary.replace(rejected_path)
    return accepted, rejected


def _quota_rows(result: SelectionResult, total: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dimension, requested, actual in (
        ("source", result.requested_sources, result.actual_sources),
        ("construction", result.requested_constructions, result.actual_constructions),
    ):
        for name, target in requested.items():
            value = actual.get(name, 0)
            rows.append({
                "dimension": dimension, "name": name, "requested": target, "actual": value,
                "requested_percent": target * 100 / total,
                "actual_percent": value * 100 / total,
            })
    return rows


def prepare_dataset(
    total: int,
    seed: int,
    output_dir: Path,
    cache_dir: Path,
    config: AppConfig,
    strict_quotas: bool = False,
    offline: bool = False,
) -> dict[str, Any]:
    blocked, blocklist_failures = _load_blocklist(config, offline)
    candidates: list[Candidate] = []
    rejected: list[dict[str, str]] = []
    source_failures: list[str] = []
    for source in config.source_percentages:
        try:
            rows, rejected_rows = _build_or_load_cache(source, config, cache_dir, offline)
            candidates.extend(rows)
            rejected.extend(rejected_rows)
        except Exception as exc:
            if strict_quotas:
                raise
            source_failures.append(f"{source}: {type(exc).__name__}: {exc}")

    unique: list[Candidate] = []
    seen: dict[str, Candidate] = {}
    signatures: dict[str, Candidate] = {}
    near_duplicates: list[dict[str, str]] = []
    for candidate in candidates:
        key = dedupe_key(candidate.ru)
        reason = "duplicate_blocklist" if key in blocked else "duplicate_across_sources" if key in seen else ""
        signature = _near_signature(candidate.ru)
        near = signatures.get(signature) if signature else None
        if not reason and near and dedupe_key(near.ru) != key:
            near_duplicates.append({
                "ru": candidate.ru, "source": candidate.source, "source_id": candidate.source_id,
                "matched_ru": near.ru, "matched_source": near.source, "signature": signature,
            })
            reason = "near_duplicate"
        if reason:
            if len(rejected) < config.max_rejected_rows:
                rejected.append({"ru": candidate.ru, "source": candidate.source, "source_id": candidate.source_id, "reason": reason})
            continue
        seen[key] = candidate
        if signature:
            signatures[signature] = candidate
        unique.append(candidate)

    main = select_candidates(
        unique, total, config.source_percentages, config.construction_percentages, seed, strict_quotas
    )
    used = {record.candidate.key for record in main.records}
    remaining = [candidate for candidate in unique if candidate.key not in used]
    desired_reserve = math.ceil(total * config.reserve_percentage / 100)
    reserve_records: tuple[SelectedRecord, ...] = ()
    reserve_shortage = desired_reserve
    if remaining and desired_reserve:
        reserve_total = min(desired_reserve, len(remaining))
        try:
            reserve_result = select_candidates(
                remaining, reserve_total, config.source_percentages,
                config.construction_percentages, seed + 1, False,
            )
            reserve_records = reserve_result.records
            reserve_shortage = desired_reserve - len(reserve_records)
        except QuotaError:
            reserve_records = ()

    manifest = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "requested_total": total,
        "actual_total": len(main.records),
        "seed": seed,
        "strict_quotas": strict_quotas,
        "reserve_requested": desired_reserve,
        "reserve_actual": len(reserve_records),
        "reserve_shortage": reserve_shortage,
        "candidate_pool": len(unique),
        "blocklist_entries": len(blocked),
        "blocklist_failures": blocklist_failures,
        "source_failures": source_failures,
        "shortages": list(main.shortages),
    }
    write_outputs(
        output_dir, main.records, reserve_records, _quota_rows(main, total),
        rejected[: config.max_rejected_rows], near_duplicates, manifest,
    )
    return manifest
