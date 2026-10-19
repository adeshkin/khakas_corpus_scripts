"""Проверка Parquet-файлов и вывод случайной строки."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

import pandas as pd


@dataclass(frozen=True)
class CheckResult:
    total: int
    valid: int
    empty: int
    failed: tuple[Path, ...]


def check_parquet_files(root: Path, *, output: TextIO) -> CheckResult:
    if not root.is_dir():
        raise NotADirectoryError(f"Путь не существует или не является каталогом: {root}")

    parquet_files = sorted(root.rglob("*.parquet"))
    valid = 0
    empty = 0
    failed: list[Path] = []

    for path in parquet_files:
        print(f"\n{path.relative_to(root)}", file=output)
        try:
            dataframe = pd.read_parquet(path)
        except Exception as error:
            failed.append(path)
            print(f"  ОШИБКА: {error}", file=output)
            continue

        valid += 1
        if dataframe.empty:
            empty += 1
            print("  файл пуст", file=output)
        else:
            print(dataframe.sample(n=1).to_string(index=False), file=output)

    return CheckResult(
        total=len(parquet_files),
        valid=valid,
        empty=empty,
        failed=tuple(failed),
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Проверить все Parquet-файлы и вывести случайную строку из каждого."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Каталог для рекурсивной проверки (по умолчанию: текущий каталог)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = check_parquet_files(args.directory, output=sys.stdout)
    except NotADirectoryError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2

    print(
        f"\nВсего: {result.total}; корректных: {result.valid}; "
        f"пустых: {result.empty}; ошибок: {len(result.failed)}"
    )
    return 1 if result.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
