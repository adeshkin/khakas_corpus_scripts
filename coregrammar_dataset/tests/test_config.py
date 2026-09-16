from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from coregrammar.config import allocate_counts, load_config, validate_total


class ConfigTests(unittest.TestCase):
    def test_total_accepts_boundaries_and_rejects_outside_range(self) -> None:
        self.assertEqual(validate_total(1), 1)
        self.assertEqual(validate_total(100_000), 100_000)
        for value in (0, 100_001):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "--total must be between 1 and 100000"):
                    validate_total(value)

    def test_allocate_counts_uses_largest_remainder(self) -> None:
        self.assertEqual(
            allocate_counts(7, {"tatoeba": 75, "common_voice": 15, "massive": 10}),
            {"tatoeba": 5, "common_voice": 1, "massive": 1},
        )
        self.assertEqual(
            allocate_counts(100_000, {"tatoeba": 75, "common_voice": 15, "massive": 10}),
            {"tatoeba": 75_000, "common_voice": 15_000, "massive": 10_000},
        )

    def test_required_total_sizes_have_exact_default_quotas(self) -> None:
        config = load_config()
        for total in (1, 100, 3_000, 10_000, 100_000):
            with self.subTest(total=total):
                self.assertEqual(total, sum(allocate_counts(total, config.source_percentages).values()))
                self.assertEqual(total, sum(allocate_counts(total, config.construction_percentages).values()))

    def test_load_config_merges_defaults_with_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "override.yaml"
            path.write_text("filters:\n  max_tokens: 12\n", encoding="utf-8")
            config = load_config(path)
        self.assertEqual(config.max_tokens, 12)
        self.assertEqual(config.source_percentages["tatoeba"], 75.0)
        self.assertEqual(sum(config.construction_percentages.values()), 100.0)


if __name__ == "__main__":
    unittest.main()
