from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Candidate:
    ru: str
    source: str
    source_id: str
    source_url: str
    license: str
    domain: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict, compare=False, hash=False)
    construction_labels: tuple[str, ...] = ()
    quality_score: float = 0.0

    @property
    def key(self) -> str:
        return f"{self.source}:{self.source_id}"


@dataclass(frozen=True, slots=True)
class SelectedRecord:
    candidate: Candidate
    primary_construction: str
    split: str = "train"
    translation_status: str = "pending"

