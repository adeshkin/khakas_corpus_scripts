#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from coregrammar.config import load_config, validate_total
from coregrammar.pipeline import prepare_dataset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare a Russian core-grammar translation queue.")
    parser.add_argument("--total", required=True, type=int, help="number of sentences (1..100000)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--cache-dir", type=Path, default=Path(__file__).resolve().parent / "cache")
    parser.add_argument("--strict-quotas", action="store_true")
    parser.add_argument("--offline", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        validate_total(args.total)  # deliberately before config loading or downloads
        config = load_config(args.config)
        manifest = prepare_dataset(
            total=args.total, seed=args.seed, output_dir=args.output,
            cache_dir=args.cache_dir, config=config,
            strict_quotas=args.strict_quotas, offline=args.offline,
        )
    except (ValueError, FileExistsError) as exc:
        parser.error(str(exc))
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
