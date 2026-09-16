from __future__ import annotations

from pathlib import Path

import pytest

from coregrammar.config import allocate_counts, load_config, validate_percentages


def test_allocate_counts_uses_largest_remainder_and_exact_total() -> None:
    assert allocate_counts(7, {"a": 50, "b": 30, "c": 20}) == {
        "a": 4,
        "b": 2,
        "c": 1,
    }


def test_allocate_counts_breaks_equal_remainders_by_input_order() -> None:
    assert allocate_counts(2, {"first": 25, "second": 25, "third": 50}) == {
        "first": 1,
        "second": 0,
        "third": 1,
    }


def test_percentages_must_sum_to_100() -> None:
    with pytest.raises(ValueError, match="sum to 100"):
        validate_percentages({"a": 60, "b": 30}, "sources")


def test_percentages_cannot_be_negative() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        validate_percentages({"a": 110, "b": -10}, "sources")


def test_load_config_reads_defaults_and_local_fixture_paths(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
sources:
  tatoeba:
    percentage: 100
    enabled: true
    local_path: /tmp/tatoeba.tsv
constructions:
  simple_clause: 100
splits:
  train: 100
filters:
  min_tokens: 3
  max_tokens: 18
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.source_percentages == {"tatoeba": 100.0}
    assert config.sources["tatoeba"].local_path == Path("/tmp/tatoeba.tsv")
    assert config.min_tokens == 3
    assert config.max_tokens == 18
