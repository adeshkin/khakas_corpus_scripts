from __future__ import annotations

import csv
import json
import math
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .models import SelectedRecord


OUTPUT_FIELDS = (
    "id", "ru", "kjh", "source", "source_id", "source_url", "license",
    "primary_construction", "construction_labels", "domain", "split",
    "translation_status",
)


def _record_dict(record: SelectedRecord, identifier: str) -> dict[str, str]:
    candidate = record.candidate
    return {
        "id": identifier,
        "ru": candidate.ru,
        "kjh": "",
        "source": candidate.source,
        "source_id": candidate.source_id,
        "source_url": candidate.source_url,
        "license": candidate.license,
        "primary_construction": record.primary_construction,
        "construction_labels": json.dumps(list(candidate.construction_labels), ensure_ascii=False),
        "domain": candidate.domain,
        "split": record.split,
        "translation_status": record.translation_status,
    }


def _write_csv(path: Path, rows: Iterable[Mapping[str, Any]], fields: Sequence[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def split_sentences_csv(
    input_path: Path,
    output_dir: Path,
    chunk_size: int = 1000,
) -> list[Path]:
    """Split a CSV into capacity-limited files stratified by source and construction."""
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if output_dir.exists():
        raise FileExistsError(f"output directory already exists: {output_dir}")

    with input_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        if fields is None:
            raise ValueError(f"CSV has no header: {input_path}")
        required = {"source", "primary_construction"}
        missing = sorted(required.difference(fields))
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")
        rows = list(reader)

    chunk_count = math.ceil(len(rows) / chunk_size)
    width = max(3, len(str(chunk_count)))
    grouped: dict[tuple[str, str], list[tuple[int, dict[str, str]]]] = defaultdict(list)
    for position, row in enumerate(rows):
        grouped[(row["source"], row["primary_construction"])].append((position, row))

    offsets = {key: 0 for key in grouped}
    remaining = {key: len(group) for key, group in grouped.items()}
    remaining_total = len(rows)
    chunks: list[list[dict[str, str]]] = []
    for _ in range(chunk_count):
        current_size = min(chunk_size, remaining_total)
        exact = {
            key: count * current_size / remaining_total
            for key, count in remaining.items()
            if count
        }
        allocation = {key: math.floor(value) for key, value in exact.items()}
        unallocated = current_size - sum(allocation.values())
        remainder_order = sorted(
            exact,
            key=lambda key: (-(exact[key] - allocation[key]), key),
        )
        for key in remainder_order[:unallocated]:
            allocation[key] += 1

        selected: list[tuple[int, dict[str, str]]] = []
        for key, count in allocation.items():
            start = offsets[key]
            stop = start + count
            selected.extend(grouped[key][start:stop])
            offsets[key] = stop
            remaining[key] -= count
        selected.sort(key=lambda item: item[0])
        chunks.append([row for _, row in selected])
        remaining_total -= current_size

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent))
    try:
        for index, chunk in enumerate(chunks, 1):
            _write_csv(temporary / f"sentences_{index:0{width}d}.csv", chunk, fields)
        temporary.replace(output_dir)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return sorted(output_dir.glob("sentences_*.csv"))


def _write_records(path: Path, records: Sequence[SelectedRecord], prefix: str) -> list[dict[str, str]]:
    width = max(6, len(str(len(records))))
    rows = [_record_dict(record, f"{prefix}-{index:0{width}d}") for index, record in enumerate(records, 1)]
    _write_csv(path, rows, OUTPUT_FIELDS)
    return rows


def write_outputs(
    output_dir: Path,
    records: Sequence[SelectedRecord],
    reserve: Sequence[SelectedRecord],
    quota_rows: Sequence[Mapping[str, Any]],
    rejected: Sequence[Mapping[str, Any]],
    near_duplicates: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Any],
) -> None:
    """Write a complete result directory and publish it with one atomic rename."""
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise FileExistsError(f"output directory already exists: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent))
    try:
        rows = _write_records(temporary / "sentences.csv", records, "cg")
        with (temporary / "sentences.jsonl").open("w", encoding="utf-8") as handle:
            for row in rows:
                payload = dict(row)
                payload["construction_labels"] = json.loads(payload["construction_labels"])
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        _write_records(temporary / "reserve.csv", reserve, "reserve")

        quota_fields = ("dimension", "name", "requested", "actual", "requested_percent", "actual_percent")
        _write_csv(temporary / "quota_report.csv", quota_rows, quota_fields)
        _write_csv(temporary / "rejected.csv", rejected, ("ru", "source", "source_id", "reason"))
        _write_csv(
            temporary / "near_duplicates.csv",
            near_duplicates,
            ("ru", "source", "source_id", "matched_ru", "matched_source", "signature"),
        )
        (temporary / "manifest.json").write_text(
            json.dumps(dict(manifest), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (temporary / "README.md").write_text(
            "# Core grammar Russian corpus\n\n"
            "`sentences.csv` and `sentences.jsonl` contain the translation queue. "
            "The `kjh` column is intentionally empty; every row has `split=train` and "
            "`translation_status=pending`. `reserve.csv` contains replacements. "
            "Quota outcomes and provenance are recorded in `quota_report.csv` and `manifest.json`.\n",
            encoding="utf-8",
        )
        temporary.replace(output_dir)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
