from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from coregrammar.classification import classify_constructions


class ClassificationTests(unittest.TestCase):
    def test_marker_categories(self) -> None:
        cases = {
            "Где находится ближайшая аптека?": "question",
            "Я сегодня не пойду на работу.": "negation_prohibition",
            "Пожалуйста, закрой окно перед уходом.": "imperative_request",
            "Мне нужно купить продукты домой.": "possession_modality_impersonal",
            "Мы приехали из города утром.": "motion_location",
            "Когда закончишь работу, позвони мне.": "temporal_aspectual",
            "Книга, которую ты дал, очень интересная.": "relative_attributive",
            "Если будет тепло, мы пойдём гулять.": "condition_cause_purpose_concession",
            "Нет, спасибо.": "dialogue_ellipsis",
        }
        for text, label in cases.items():
            with self.subTest(text=text):
                self.assertIn(label, classify_constructions(text))

    def test_plain_sentence_falls_back_to_simple_clause(self) -> None:
        self.assertEqual(classify_constructions("Мальчик читает новую книгу."), ("simple_clause",))


if __name__ == "__main__":
    unittest.main()
