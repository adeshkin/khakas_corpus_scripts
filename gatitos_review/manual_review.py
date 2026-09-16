#!/usr/bin/env python3
"""Interactively validate Russian and Khakas translations in random order."""

from __future__ import annotations

import argparse
import csv
import fcntl
import os
import random
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, TextIO


REQUIRED_COLUMNS = [
    "en",
    "ru_corrected",
    "kjh_from_ru_by_yandex",
    "kjh_corrected",
]
MANUAL_COLUMNS = [
    "ru_manually_corrected",
    "kjh_manually_corrected",
    "manual_reviewed",
]


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        duplicates = sorted(
            {column for column in fieldnames if fieldnames.count(column) > 1}
        )
        if duplicates:
            raise ValueError(f"duplicate columns: {', '.join(duplicates)}")
        missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
        if missing:
            raise ValueError(f"missing required columns: {', '.join(missing)}")
        rows = list(reader)

    for number, row in enumerate(rows, start=2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"{path.name}:{number}: malformed CSV row")
    return fieldnames, rows


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    """Replace a CSV atomically so interruption cannot leave a partial file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_name = handle.name
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
                lineterminator="\n",
                extrasaction="raise",
            )
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def initialize_review_file(source: Path, destination: Path) -> None:
    fieldnames, rows = _read_csv(source)
    for column in MANUAL_COLUMNS:
        if column not in fieldnames:
            fieldnames.append(column)
        for row in rows:
            row.setdefault(column, "")
    _write_csv(destination, fieldnames, rows)


@contextmanager
def _review_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(f".{path.name}.lock")
    with lock_path.open("w") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError(f"{path.name} is already being reviewed") from error
        yield


def _answer_or_default(answer: str, default: str) -> str:
    answer = answer.strip()
    if answer.casefold() == "/empty":
        return ""
    return answer or default


def _confirm_value(
    label: str,
    default: str,
    *,
    input_fn: Callable[[str], str],
    output: TextIO,
) -> str:
    answer = input_fn("ok? ")
    if not answer.strip():
        return default

    candidate = _answer_or_default(answer, default)
    while True:
        output.write(f"Теперь {label}: {candidate or '(пусто)'}\n")
        answer = input_fn("ok? ")
        if not answer.strip():
            return candidate
        candidate = _answer_or_default(answer, candidate)


def review_file(
    path: Path,
    *,
    input_fn: Callable[[str], str] = input,
    output: TextIO = sys.stdout,
    shuffle_fn: Callable[[list[int]], None] = random.shuffle,
) -> int:
    """Review pending rows in ``path`` and return the number completed."""
    with _review_lock(path):
        return _review_file_unlocked(
            path,
            input_fn=input_fn,
            output=output,
            shuffle_fn=shuffle_fn,
        )


def _review_file_unlocked(
    path: Path,
    *,
    input_fn: Callable[[str], str],
    output: TextIO,
    shuffle_fn: Callable[[list[int]], None],
) -> int:
    fieldnames, rows = _read_csv(path)
    columns_added = False
    for column in MANUAL_COLUMNS:
        if column not in fieldnames:
            fieldnames.append(column)
            columns_added = True
        for row in rows:
            row.setdefault(column, "")
    if columns_added:
        _write_csv(path, fieldnames, rows)

    pending = [
        index
        for index, row in enumerate(rows)
        if row["manual_reviewed"].strip().casefold() != "yes"
    ]
    shuffle_fn(pending)
    completed = 0

    try:
        for position, index in enumerate(pending, start=1):
            row = rows[index]
            output.write(f"\n[{position}/{len(pending)}] EN: {row['en']}\n")
            output.write(f"RU: {row['ru_corrected']}\n")
            accepted_russian = _confirm_value(
                "RU",
                row["ru_corrected"],
                input_fn=input_fn,
                output=output,
            )

            output.write("\n")
            output.write(f"EN: {row['en']}\n")
            output.write(f"RU: {accepted_russian}\n")
            output.write(f"Yandex KJH: {row['kjh_from_ru_by_yandex']}\n")
            output.write(f"KJH corrected: {row['kjh_corrected']}\n")
            row["ru_manually_corrected"] = accepted_russian
            row["kjh_manually_corrected"] = _confirm_value(
                "KJH",
                row["kjh_corrected"],
                input_fn=input_fn,
                output=output,
            )
            row["manual_reviewed"] = "yes"
            _write_csv(path, fieldnames, rows)
            completed += 1
            output.write("Сохранено.\n")
    except (KeyboardInterrupt, EOFError):
        output.write("\nПроверка остановлена. Уже завершённые строки сохранены.\n")

    remaining = len(pending) - completed
    output.write(f"Готово за этот запуск: {completed}. Осталось: {remaining}.\n")
    return completed


def _default_output_path(source: Path) -> Path:
    return source.with_name(f"{source.stem}_manually_reviewed{source.suffix}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent / "gatitos_en_ru_kjh_reviewed.csv",
        help="исходный CSV (по умолчанию gatitos_en_ru_kjh_reviewed.csv)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="файл результата (по умолчанию *_manually_reviewed.csv)",
    )
    parser.add_argument("--seed", type=int, help="seed для воспроизводимого порядка")
    args = parser.parse_args()

    source = args.input.resolve()
    destination = (args.output or _default_output_path(source)).resolve()
    shuffle = random.Random(args.seed).shuffle if args.seed is not None else random.shuffle
    try:
        with _review_lock(destination):
            if not destination.exists():
                initialize_review_file(source, destination)
            _review_file_unlocked(
                destination,
                input_fn=input,
                output=sys.stdout,
                shuffle_fn=shuffle,
            )
    except (OSError, RuntimeError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
