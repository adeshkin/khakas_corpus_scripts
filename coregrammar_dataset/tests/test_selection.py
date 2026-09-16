from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from coregrammar.models import Candidate
from coregrammar.selection import QuotaError, select_candidates


def make_candidate(source: str, label: str, index: int) -> Candidate:
    return Candidate(
        ru=f"Это русское предложение номер {source} {label} {index}.",
        source=source,
        source_id=f"{source}-{label}-{index}",
        source_url="https://example.test",
        license="CC BY 4.0",
        construction_labels=(label,),
        quality_score=1.0,
    )


class SelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sources = {"tatoeba": 75, "common_voice": 15, "massive": 10}
        self.constructions = {"simple_clause": 60, "question": 40}
        self.pool = [
            make_candidate(source, label, index)
            for source in self.sources
            for label in self.constructions
            for index in range(30)
        ]

    def test_selection_is_deterministic_and_meets_both_quotas(self) -> None:
        first = select_candidates(self.pool, 20, self.sources, self.constructions, seed=7, strict=True)
        second = select_candidates(self.pool, 20, self.sources, self.constructions, seed=7, strict=True)
        self.assertEqual(
            [row.candidate.source_id for row in first.records],
            [row.candidate.source_id for row in second.records],
        )
        self.assertEqual(first.actual_sources, {"tatoeba": 15, "common_voice": 3, "massive": 2})
        self.assertEqual(first.actual_constructions, {"simple_clause": 12, "question": 8})

    def test_strict_mode_reports_unfillable_source_quota(self) -> None:
        pool = [row for row in self.pool if row.source != "massive"]
        with self.assertRaises(QuotaError) as context:
            select_candidates(pool, 20, self.sources, self.constructions, seed=7, strict=True)
        self.assertIn("massive", str(context.exception))

    def test_non_strict_mode_redistributes_missing_source(self) -> None:
        pool = [row for row in self.pool if row.source != "massive"]
        result = select_candidates(pool, 20, self.sources, self.constructions, seed=7, strict=False)
        self.assertEqual(len(result.records), 20)
        self.assertEqual(result.actual_sources["massive"], 0)
        self.assertTrue(result.shortages)


if __name__ == "__main__":
    unittest.main()
