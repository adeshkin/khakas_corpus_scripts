"""Download every Hugging Face dataset repository owned by an author."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TextIO


@dataclass(frozen=True)
class DownloadResult:
    downloaded: int
    failed: tuple[str, ...]


def download_all_datasets(
    *,
    author: str,
    output_dir: Path,
    token: str | None = None,
    api: Any | None = None,
    downloader: Callable[..., object] | None = None,
    output: TextIO = sys.stdout,
) -> DownloadResult:
    """Download all dataset repositories belonging to ``author``."""
    if api is None or downloader is None:
        from huggingface_hub import HfApi, snapshot_download

        api = api or HfApi(token=token)
        downloader = downloader or snapshot_download

    datasets = list(api.list_datasets(author=author))
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Найдено датасетов: {len(datasets)}", file=output)
    downloaded = 0
    failed: list[str] = []

    for number, dataset in enumerate(datasets, start=1):
        repo_id = dataset.id
        destination = output_dir / repo_id.rsplit("/", 1)[-1]
        print(f"[{number}/{len(datasets)}] {repo_id} -> {destination}", file=output)

        try:
            downloader(
                repo_id=repo_id,
                repo_type="dataset",
                local_dir=destination,
                token=token,
            )
        except Exception as error:  # Continue downloading the remaining repositories.
            failed.append(repo_id)
            print(f"  Ошибка: {error}", file=output)
        else:
            downloaded += 1

    print(f"Скачано: {downloaded}; ошибок: {len(failed)}", file=output)
    return DownloadResult(downloaded=downloaded, failed=tuple(failed))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Скачать все датасеты пользователя с Hugging Face Hub."
    )
    parser.add_argument("--author", default="adeshkin", help="Автор датасетов")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("datasets"),
        help="Каталог для скачивания (по умолчанию: ./datasets)",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("HF_TOKEN"),
        help="Hugging Face token (по умолчанию берётся из HF_TOKEN)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = download_all_datasets(
        author=args.author,
        output_dir=args.output_dir,
        token=args.token,
    )
    return 1 if result.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
