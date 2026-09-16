from __future__ import annotations

import bz2
import csv
import hashlib
import json
import re
import shutil
import urllib.request
from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import Any

from .config import SourceConfig
from .models import Candidate


TATOEBA_SOURCE_URL = "https://tatoeba.org"
COMMON_VOICE_SOURCE_URL = "https://github.com/common-voice/common-voice"
MASSIVE_SOURCE_URL = "https://huggingface.co/datasets/AmazonScience/massive"


def _text_reader(path: Path):
    if path.suffix == ".bz2":
        return bz2.open(path, "rt", encoding="utf-8", newline="")
    return path.open("r", encoding="utf-8", newline="")


def parse_native_users(path: Path, language: str = "rus") -> set[str]:
    native: set[str] = set()
    with _text_reader(path) as handle:
        for row in csv.reader(handle, delimiter="\t"):
            if language not in row or "5" not in row:
                continue
            language_index = row.index(language)
            level_index = row.index("5")
            remaining = [value for index, value in enumerate(row) if index not in (language_index, level_index)]
            if remaining and remaining[0] and remaining[0] != r"\N":
                native.add(remaining[0])
    return native


def parse_tatoeba(path: Path, native_users: set[str] | None = None) -> Iterator[Candidate]:
    with _text_reader(path) as handle:
        for row in csv.reader(handle, delimiter="\t"):
            if len(row) < 3:
                continue
            sentence_id = row[0]
            if re.fullmatch(r"[a-z]{3}", row[1]):  # generic detailed export
                if row[1] != "rus":
                    continue
                text = row[2]
                owner = row[3] if len(row) > 3 else ""
            else:  # per-language detailed export: id, text, owner, ...
                text = row[1]
                owner = row[2] if len(row) > 2 else ""
            is_native = owner in native_users if native_users is not None else False
            yield Candidate(
                ru=text,
                source="tatoeba",
                source_id=sentence_id,
                source_url=f"{TATOEBA_SOURCE_URL}/rus/sentences/show/{sentence_id}",
                license="CC BY 2.0 FR",
                domain="general",
                metadata={"owner": owner, "native_author": is_native},
                quality_score=0.15 if is_native else 0.0,
            )


def parse_common_voice(path: Path) -> Iterator[Candidate]:
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            text = line.strip()
            if not text:
                continue
            yield Candidate(
                ru=text,
                source="common_voice",
                source_id=f"line-{line_number}",
                source_url=COMMON_VOICE_SOURCE_URL,
                license="CC0-1.0",
                domain="general",
            )


def parse_massive_rows(rows: Iterable[Mapping[str, Any]]) -> Iterator[Candidate]:
    for index, row in enumerate(rows):
        if row.get("locale", "ru-RU") != "ru-RU":
            continue
        text = row.get("utt") or row.get("text")
        if not text:
            continue
        source_id = str(row.get("id", row.get("worker_id", index)))
        scenario = str(row.get("scenario", "unknown"))
        intent = str(row.get("intent", "unknown"))
        yield Candidate(
            ru=str(text),
            source="massive",
            source_id=source_id,
            source_url=MASSIVE_SOURCE_URL,
            license="CC BY 4.0",
            domain=scenario,
            metadata={"intent": intent, "annot_utt": row.get("annot_utt", "")},
        )


def download_cached(url: str, destination: Path, offline: bool = False) -> Path:
    if destination.exists():
        return destination
    if offline:
        raise FileNotFoundError(f"offline cache miss: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "khakas-coregrammar/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as output:
            shutil.copyfileobj(response, output)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _decode_class_labels(dataset: Any, row: Mapping[str, Any]) -> dict[str, Any]:
    decoded = dict(row)
    features = getattr(dataset, "features", None)
    if not features:
        return decoded
    for name in ("scenario", "intent"):
        value = decoded.get(name)
        feature = features.get(name) if hasattr(features, "get") else None
        if isinstance(value, int) and feature is not None and hasattr(feature, "int2str"):
            decoded[name] = feature.int2str(value)
    return decoded


def load_massive(config: SourceConfig, offline: bool = False) -> Iterator[Candidate]:
    try:
        from datasets import DownloadConfig, load_dataset
    except ImportError as exc:
        raise RuntimeError("MASSIVE requires `pip install datasets`") from exc
    download_config = DownloadConfig(local_files_only=offline)
    for split in ("train", "validation", "test"):
        dataset = load_dataset(
            "AmazonScience/massive",
            "ru-RU",
            split=split,
            streaming=True,
            revision=config.revision,
            download_config=download_config,
        )
        yield from parse_massive_rows(_decode_class_labels(dataset, row) for row in dataset)


def load_source(
    name: str,
    config: SourceConfig,
    cache_dir: Path,
    offline: bool = False,
) -> Iterator[Candidate]:
    raw_dir = cache_dir / "raw"
    if config.local_path:
        path = Path(config.local_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"local source does not exist: {path}")
        if name == "tatoeba":
            native_users = parse_native_users(Path(config.native_users_path)) if config.native_users_path else None
            return parse_tatoeba(path, native_users)
        if name == "common_voice":
            return parse_common_voice(path)
        if name == "massive":
            with path.open(encoding="utf-8") as handle:
                return parse_massive_rows(json.loads(line) for line in handle if line.strip())
    if name == "tatoeba":
        if not config.url:
            raise ValueError("tatoeba source URL is missing")
        path = download_cached(config.url, raw_dir / "rus_sentences_detailed.tsv.bz2", offline)
        native_users = None
        if config.native_users_url:
            users_path = download_cached(
                config.native_users_url, raw_dir / "rus_user_languages.tsv.bz2", offline
            )
            native_users = parse_native_users(users_path)
        return parse_tatoeba(path, native_users)
    if name == "common_voice":
        if not config.url:
            raise ValueError("common_voice source URL is missing")
        path = download_cached(config.url, raw_dir / "common_voice_ru.txt", offline)
        return parse_common_voice(path)
    if name == "massive":
        return load_massive(config, offline)
    raise ValueError(f"unknown source: {name}")


def iter_jsonl_candidates(path: Path) -> Iterator[Candidate]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            data = json.loads(line)
            data["construction_labels"] = tuple(data.get("construction_labels", ()))
            yield Candidate(**data)


def write_jsonl_candidates(path: Path, candidates: Iterable[Candidate]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    count = 0
    with temporary.open("w", encoding="utf-8") as handle:
        for candidate in candidates:
            payload = {
                "ru": candidate.ru,
                "source": candidate.source,
                "source_id": candidate.source_id,
                "source_url": candidate.source_url,
                "license": candidate.license,
                "domain": candidate.domain,
                "metadata": candidate.metadata,
                "construction_labels": list(candidate.construction_labels),
                "quality_score": candidate.quality_score,
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            count += 1
    temporary.replace(path)
    return count
