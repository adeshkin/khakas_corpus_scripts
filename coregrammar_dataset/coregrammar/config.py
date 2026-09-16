from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import yaml


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.default.yaml"


@dataclass(frozen=True, slots=True)
class SourceConfig:
    percentage: float
    enabled: bool = True
    revision: str | None = None
    url: str | None = None
    local_path: str | None = None
    native_users_url: str | None = None
    native_users_path: str | None = None


@dataclass(frozen=True, slots=True)
class AppConfig:
    sources: dict[str, SourceConfig]
    constructions: dict[str, float]
    min_tokens: int = 4
    max_tokens: int = 18
    dialogue_min_tokens: int = 2
    cyrillic_ratio: float = 0.8
    reserve_percentage: float = 20.0
    oversample_factor: float = 3.0
    max_rejected_rows: int = 100_000
    blocked_terms: tuple[str, ...] = ()
    blocklist_datasets: tuple[dict[str, Any], ...] = ()

    @property
    def source_percentages(self) -> dict[str, float]:
        return {name: cfg.percentage for name, cfg in self.sources.items() if cfg.enabled}

    @property
    def construction_percentages(self) -> dict[str, float]:
        return dict(self.constructions)


def validate_total(total: int) -> int:
    if isinstance(total, bool) or not isinstance(total, int) or not 1 <= total <= 100_000:
        raise ValueError("--total must be between 1 and 100000")
    return total


def validate_percentages(values: Mapping[str, float], name: str) -> None:
    if not values:
        raise ValueError(f"{name} percentages cannot be empty")
    if any(value < 0 for value in values.values()):
        raise ValueError(f"{name} percentages must be non-negative")
    if not math.isclose(sum(values.values()), 100.0, abs_tol=1e-8):
        raise ValueError(f"{name} percentages must sum to 100")


def allocate_counts(total: int, percentages: Mapping[str, float]) -> dict[str, int]:
    validate_total(total)
    validate_percentages(percentages, "quota")
    raw = {name: total * value / 100.0 for name, value in percentages.items()}
    result = {name: math.floor(value) for name, value in raw.items()}
    remainder = total - sum(result.values())
    order = sorted(raw, key=lambda name: (-(raw[name] - result[name]), list(raw).index(name)))
    for name in order[:remainder]:
        result[name] += 1
    return result


def _deep_merge(base: dict[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _deep_merge(dict(merged[key]), value)
        else:
            merged[key] = value
    return merged


def load_config(path: Path | str | None = None) -> AppConfig:
    with DEFAULT_CONFIG_PATH.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if path is not None:
        with Path(path).open(encoding="utf-8") as handle:
            data = _deep_merge(data, yaml.safe_load(handle) or {})

    sources = {
        name: SourceConfig(
            percentage=float(item["percentage"]),
            enabled=bool(item.get("enabled", True)),
            revision=item.get("revision"),
            url=item.get("url"),
            local_path=item.get("local_path"),
            native_users_url=item.get("native_users_url"),
            native_users_path=item.get("native_users_path"),
        )
        for name, item in data["sources"].items()
    }
    constructions = {name: float(value) for name, value in data["constructions"].items()}
    validate_percentages({n: s.percentage for n, s in sources.items() if s.enabled}, "source")
    validate_percentages(constructions, "construction")
    filters = data.get("filters", {})
    output = data.get("output", {})
    return AppConfig(
        sources=sources,
        constructions=constructions,
        min_tokens=int(filters.get("min_tokens", 4)),
        max_tokens=int(filters.get("max_tokens", 18)),
        dialogue_min_tokens=int(filters.get("dialogue_min_tokens", 2)),
        cyrillic_ratio=float(filters.get("cyrillic_ratio", 0.8)),
        reserve_percentage=float(output.get("reserve_percentage", 20)),
        oversample_factor=float(data.get("selection", {}).get("oversample_factor", 3)),
        max_rejected_rows=int(output.get("max_rejected_rows", 100_000)),
        blocked_terms=tuple(filters.get("blocked_terms", ())),
        blocklist_datasets=tuple(data.get("blocklists", ())),
    )
