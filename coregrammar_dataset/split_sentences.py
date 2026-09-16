#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from coregrammar.output import split_sentences_csv


DEFAULT_INPUT = (
    Path(__file__).resolve().parent
    / "coregrammar_dataset/output/coregrammar_100000/sentences.csv"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Split sentences.csv into stratified CSV files while preserving "
            "source and primary-construction proportions."
        )
    )
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--chunk-size", type=int, default=1000)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    output = args.output or args.input.parent / "sentences_100"
    try:
        paths = split_sentences_csv(args.input, output, chunk_size=args.chunk_size)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Created {len(paths)} CSV files in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
