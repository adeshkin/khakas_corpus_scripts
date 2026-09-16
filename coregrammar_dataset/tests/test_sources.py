from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"
sys.path.insert(0, str(PROJECT_DIR))

from coregrammar.sources import parse_common_voice, parse_massive_rows, parse_native_users, parse_tatoeba


class SourceParserTests(unittest.TestCase):
    def test_tatoeba_parser_keeps_only_russian_and_owner(self) -> None:
        rows = list(parse_tatoeba(FIXTURES / "tatoeba.tsv"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].ru, "Когда вернёшься домой, позвони мне.")
        self.assertEqual(rows[0].metadata["owner"], "native_user")
        self.assertEqual(rows[0].source_id, "1001")

    def test_tatoeba_native_authors_receive_priority_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            users = Path(tmp) / "users.tsv"
            users.write_text("rus\t5\tnative_user\tNative speaker\n", encoding="utf-8")
            native = parse_native_users(users)
        rows = list(parse_tatoeba(FIXTURES / "tatoeba.tsv", native))
        self.assertTrue(rows[0].metadata["native_author"])
        self.assertGreater(rows[0].quality_score, 0)

    def test_common_voice_parser_creates_stable_line_ids(self) -> None:
        rows = list(parse_common_voice(FIXTURES / "common_voice.txt"))
        self.assertEqual([row.source_id for row in rows], ["line-1", "line-2"])
        self.assertTrue(all(row.license == "CC0-1.0" for row in rows))

    def test_massive_parser_preserves_scenario_and_intent(self) -> None:
        with (FIXTURES / "massive.jsonl").open(encoding="utf-8") as handle:
            raw = [json.loads(line) for line in handle]
        rows = list(parse_massive_rows(raw))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].domain, "alarm")
        self.assertEqual(rows[0].metadata["intent"], "alarm_set")


if __name__ == "__main__":
    unittest.main()
