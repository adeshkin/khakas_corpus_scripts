from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from coregrammar.config import load_config
from coregrammar.filtering import dedupe_key, evaluate_candidate, normalize_display
from coregrammar.models import Candidate


def candidate(text: str, source: str = "tatoeba") -> Candidate:
    return Candidate(text, source, "1", "https://example.test", "CC BY 2.0")


class FilteringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config()

    def test_display_normalization_preserves_letters_and_compacts_space(self) -> None:
        self.assertEqual(normalize_display("  Всё\u00a0  дома!  "), "Всё дома!")

    def test_dedupe_key_ignores_case_yo_and_terminal_punctuation(self) -> None:
        self.assertEqual(dedupe_key("Всё дома!"), dedupe_key("все дома"))

    def test_rejects_non_russian_markup_url_and_length(self) -> None:
        cases = {
            "Visit https://example.com now": "url",
            "<b>Обычное русское предложение здесь.</b>": "markup",
            "This is an English sentence.": "not_russian",
            "Очень коротко.": "too_short",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                result = evaluate_candidate(candidate(text), self.config)
                self.assertEqual(result.rejection_reason, expected)

    def test_accepts_short_dialogue_reply(self) -> None:
        result = evaluate_candidate(candidate("Нет, спасибо."), self.config)
        self.assertIsNone(result.rejection_reason)
        self.assertIn("dialogue_ellipsis", result.candidate.construction_labels)

    def test_common_voice_officialese_is_rejected(self) -> None:
        result = evaluate_candidate(
            candidate("Организация Объединенных Наций приняла важное решение.", "common_voice"),
            self.config,
        )
        self.assertEqual(result.rejection_reason, "blocked_register")

    def test_rejects_lists_poetry_and_common_voice_speech_register(self) -> None:
        cases = (
            ("1. Сначала откройте дверь и войдите внутрь.", "tatoeba", "list_item"),
            ("Первая строка тихо звучит.\nВторая строка ей отвечает.", "tatoeba", "line_break"),
            ("Уважаемые депутаты, господин председатель открыл заседание.", "common_voice", "blocked_register"),
        )
        for text, source, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(evaluate_candidate(candidate(text, source), self.config).rejection_reason, expected)


if __name__ == "__main__":
    unittest.main()
