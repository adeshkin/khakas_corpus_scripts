import csv
import fcntl
import importlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

import review_gatitos as rg


class ReviewGatitosTests(unittest.TestCase):
    def test_manual_review_accepts_defaults_and_saves_completed_row(self):
        mr = self._manual_review_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.csv"
            self._write(path, [
                ["en", "ru_corrected", "kjh_from_ru_by_yandex", "kjh_corrected"],
                ["Hello", "Привет", "Изен", "изен"],
            ])

            answers = iter(["", ""])
            prompts = []
            output = io.StringIO()
            completed = mr.review_file(
                path,
                input_fn=lambda prompt: prompts.append(prompt) or next(answers),
                output=output,
            )

            with path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(completed, 1)
            self.assertEqual(rows[0]["ru_manually_corrected"], "Привет")
            self.assertEqual(rows[0]["kjh_manually_corrected"], "изен")
            self.assertEqual(rows[0]["manual_reviewed"], "yes")
            self.assertEqual(prompts, ["ok? ", "ok? "])
            self.assertIn("EN: Hello", output.getvalue())
            self.assertIn("Yandex KJH: Изен", output.getvalue())

    def test_manual_review_uses_typed_corrections_and_skips_reviewed_rows(self):
        mr = self._manual_review_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.csv"
            self._write(path, [
                [
                    "en", "ru_corrected", "kjh_from_ru_by_yandex", "kjh_corrected",
                    "ru_manually_corrected", "kjh_manually_corrected", "manual_reviewed",
                ],
                ["Done", "Готово", "Тимде", "тимде", "Готово", "тимде", "yes"],
                ["Cat", "Кошка", "Пиис", "пиис", "", "", ""],
            ])

            answers = iter(["кот", "", "пӱӱр", ""])
            output = io.StringIO()
            completed = mr.review_file(
                path,
                input_fn=lambda _prompt: next(answers),
                output=output,
            )

            with path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(completed, 1)
            self.assertNotIn("EN: Done", output.getvalue())
            self.assertEqual(rows[1]["ru_manually_corrected"], "кот")
            self.assertEqual(rows[1]["kjh_manually_corrected"], "пӱӱр")
            self.assertIn("Теперь RU: кот", output.getvalue())
            self.assertIn("Теперь KJH: пӱӱр", output.getvalue())

    def test_manual_review_allows_fixing_a_typo_before_confirmation(self):
        mr = self._manual_review_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.csv"
            self._write(path, [
                ["en", "ru_corrected", "kjh_from_ru_by_yandex", "kjh_corrected"],
                ["Cat", "Кошка", "Пиис", "пиис"],
            ])
            answers = iter(["кошкаа", "кошка", "", ""])

            mr.review_file(
                path,
                input_fn=lambda _prompt: next(answers),
                output=io.StringIO(),
            )

            with path.open(encoding="utf-8", newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row["ru_manually_corrected"], "кошка")

    def test_manual_review_keeps_prior_progress_when_interrupted(self):
        mr = self._manual_review_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.csv"
            self._write(path, [
                ["en", "ru_corrected", "kjh_from_ru_by_yandex", "kjh_corrected"],
                ["One", "Один", "Пір", "пір"],
                ["Two", "Два", "Ікі", "ікі"],
            ])
            answers = iter(["", "", KeyboardInterrupt()])

            def interrupting_input(_prompt):
                answer = next(answers)
                if isinstance(answer, BaseException):
                    raise answer
                return answer

            completed = mr.review_file(
                path,
                input_fn=interrupting_input,
                output=io.StringIO(),
                shuffle_fn=lambda indexes: None,
            )

            with path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(completed, 1)
            self.assertEqual(rows[0]["manual_reviewed"], "yes")
            self.assertEqual(rows[1]["manual_reviewed"], "")

    def test_manual_review_rejects_csv_without_required_columns(self):
        mr = self._manual_review_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.csv"
            self._write(path, [["en", "ru_corrected"], ["Cat", "Кошка"]])

            with self.assertRaisesRegex(ValueError, "missing required columns"):
                mr.review_file(path, input_fn=lambda _prompt: "", output=io.StringIO())

    def test_manual_review_rejects_duplicate_headers_before_rewriting(self):
        mr = self._manual_review_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.csv"
            original = (
                "en,ru_corrected,kjh_from_ru_by_yandex,kjh_corrected,en\n"
                "Cat,Кошка,Пиис,пиис,Duplicate\n"
            )
            path.write_text(original, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "duplicate columns"):
                mr.review_file(path, input_fn=lambda _prompt: "", output=io.StringIO())
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_manual_review_empty_command_clears_a_translation(self):
        mr = self._manual_review_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.csv"
            self._write(path, [
                ["en", "ru_corrected", "kjh_from_ru_by_yandex", "kjh_corrected"],
                ["The", "Артикль", "Ол", "ол"],
            ])

            answers = iter(["", "/empty", ""])
            mr.review_file(
                path,
                input_fn=lambda _prompt: next(answers),
                output=io.StringIO(),
            )

            with path.open(encoding="utf-8", newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row["ru_manually_corrected"], "Артикль")
            self.assertEqual(row["kjh_manually_corrected"], "")
            self.assertEqual(row["manual_reviewed"], "yes")

    def test_manual_review_refuses_a_second_writer(self):
        mr = self._manual_review_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.csv"
            self._write(path, [
                ["en", "ru_corrected", "kjh_from_ru_by_yandex", "kjh_corrected"],
                ["Cat", "Кошка", "Пиис", "пиис"],
            ])
            lock_path = path.with_name(f".{path.name}.lock")
            with lock_path.open("w") as lock_handle:
                fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                with self.assertRaisesRegex(RuntimeError, "already being reviewed"):
                    mr.review_file(
                        path,
                        input_fn=lambda _prompt: "",
                        output=io.StringIO(),
                    )

    def test_normalize_lookup_is_conservative(self):
        self.assertEqual(rg.normalize_lookup("  Ёлка,  да! "), "елка да")
        self.assertEqual(rg.normalize_lookup("тоос- саларға"), "тоос саларға")

    def test_collects_candidates_in_source_order_and_deduplicates(self):
        indexes = rg.SourceIndexes(
            base={"слово": ["изен", "изен"]},
            khakas_russian={"слово": ["изен", "изеннер"]},
            explanatory={"слово": ["ИЗЕН", "описательное-слово"]},
            literary={},
        )
        candidates, sources = rg.collect_candidates("слово", indexes)
        self.assertEqual(candidates, ["изен", "изеннер"])
        self.assertEqual(
            sources,
            [
                "russian-khakas-base-phrases",
                "khakas-explanatory-dict",
                "khakas-russian-dict",
            ],
        )

    def test_confirmed_yandex_variant_is_first_after_sense_filtering(self):
        indexes = rg.SourceIndexes(
            base={"слово": ["а"]},
            khakas_russian={"слово": ["г"]},
            explanatory={"слово": ["б"]},
            literary={"слово": ["в"]},
            khakas_senses={
                "а": ["слово"], "б": ["слово"], "в": ["слово"], "г": ["слово"],
            },
        )
        result = rg.review_row(
            {"en": "word", "ru_from_en_by_google": "слово", "kjh_from_ru_by_yandex": "г"},
            indexes,
        )
        self.assertEqual(result["kjh_corrected"], "г; а; б; в")
        self.assertEqual(
            result["kjh_sources"],
            "russian-khakas-base-phrases; khakas-explanatory-dict; "
            "russian-khakas-literary-dict; khakas-russian-dict",
        )
        self.assertIn("yandex_promoted", result["review_flags"])

    def test_fourth_sense_is_removed_but_one_fallback_survives(self):
        mixed = rg.SourceIndexes(
            base={"слово": ["первый", "дальний"]},
            khakas_russian={}, explanatory={}, literary={},
            khakas_senses={
                "первый": ["другое", "слово"],
                "дальний": ["раз", "два", "три", "слово"],
            },
        )
        result = rg.review_row(
            {"en": "word", "ru_from_en_by_google": "слово", "kjh_from_ru_by_yandex": ""},
            mixed,
        )
        self.assertEqual(result["kjh_corrected"], "первый")

        fallback = rg.SourceIndexes(
            base={"слово": ["дальний"]},
            khakas_russian={}, explanatory={}, literary={},
            khakas_senses={"дальний": ["раз", "два", "три", "слово"]},
        )
        result = rg.review_row(
            {"en": "word", "ru_from_en_by_google": "слово", "kjh_from_ru_by_yandex": ""},
            fallback,
        )
        self.assertEqual(result["kjh_corrected"], "дальний")
        self.assertEqual(result["review_status"], "unverified_source")
        self.assertEqual(result["native_review"], "required")
        self.assertIn("sense_rank_over_3", result["review_flags"])

    def test_function_words_use_grammatical_metadata(self):
        indexes = rg.SourceIndexes(
            base={"для": ["ӱчӱн"]}, khakas_russian={}, explanatory={}, literary={},
            khakas_senses={"ӱчӱн": ["для"]},
        )
        article = rg.review_row(
            {"en": "the", "ru_from_en_by_google": "тот", "kjh_from_ru_by_yandex": "тігізі"},
            indexes,
        )
        self.assertEqual(article["kjh_corrected"], "")
        self.assertEqual(article["function_word_handling"], "omitted")
        self.assertEqual(article["review_status"], "grammatical")

        locative = rg.review_row(
            {"en": "in", "ru_from_en_by_google": "в", "kjh_from_ru_by_yandex": "в"},
            indexes,
        )
        self.assertEqual(locative["kjh_corrected"], "")
        self.assertEqual(locative["function_word_handling"], "case_suffix")
        self.assertEqual(locative["native_review"], "required")

        postposition = rg.review_row(
            {"en": "for", "ru_from_en_by_google": "для", "kjh_from_ru_by_yandex": "ӱчӱн"},
            indexes,
        )
        self.assertEqual(postposition["kjh_corrected"], "ӱчӱн")
        self.assertEqual(postposition["function_word_handling"], "postposition")

    def test_generic_for_rejects_adverbial_for_interest_candidate(self):
        indexes = rg.SourceIndexes(
            base={},
            khakas_russian={"для": ["ӱчӱн", "хыныға"]},
            explanatory={}, literary={},
            khakas_senses={
                "ӱчӱн": ["ради; за; для"],
                "хыныға": ["ради интереса; для; ради интереса"],
            },
        )
        result = rg.review_row(
            {"en": "for", "ru_from_en_by_google": "для", "kjh_from_ru_by_yandex": "ӱчӱн"},
            indexes,
        )
        self.assertEqual(result["kjh_corrected"], "ӱчӱн")

    def test_changed_russian_does_not_revive_conflicting_yandex_dictionary_word(self):
        indexes = rg.SourceIndexes(
            base={}, khakas_russian={}, explanatory={}, literary={},
            khakas_senses={"хой": ["овца"]},
        )
        result = rg.review_row(
            {"en": "Ewe", "ru_from_en_by_google": "Овца", "kjh_from_ru_by_yandex": "Хой"},
            indexes,
        )
        self.assertEqual(result["kjh_corrected"], "")
        self.assertEqual(result["review_status"], "missing")

    def test_frequency_review_flags_shared_khakas_word(self):
        rows = [
            self._reviewed_stub("fine", "отлично", "хандыра"),
            self._reviewed_stub("magnificent", "великолепный", "хандыра"),
            self._reviewed_stub("deep", "глубокий", "тирең"),
        ]
        reviewed = rg.apply_frequency_review(rows)
        self.assertEqual(reviewed[0]["frequent_kjh"], "хандыра (2 строк / 2 RU)")
        self.assertEqual(reviewed[1]["frequent_kjh"], "хандыра (2 строк / 2 RU)")
        self.assertEqual(reviewed[0]["native_review"], "recommended")
        self.assertEqual(reviewed[2]["frequent_kjh"], "")

    def test_verb_candidates_keep_infinitives_only(self):
        indexes = rg.SourceIndexes(
            base={},
            khakas_russian={"завершать": ["тоозарға", "тоосча", "тӱгедерге"]},
            explanatory={},
            literary={},
        )
        candidates, _ = rg.collect_candidates("завершать", indexes)
        self.assertEqual(candidates, ["тоозарға", "тӱгедерге"])

    def test_curated_article_evidence_adds_completion_synonym(self):
        indexes = rg.SourceIndexes(
            base={},
            khakas_russian={},
            explanatory={"завершать": ["тоозарға"]},
            literary={},
        )
        candidates, sources = rg.collect_candidates("завершать", indexes)
        self.assertEqual(candidates, ["тоозарға", "тӱгедерге"])
        self.assertEqual(
            sources,
            ["khakas-explanatory-dict", "khakas-russian-dict"],
        )

    def test_control_rows_apply_review_policy(self):
        indexes = rg.SourceIndexes(
            base={"привет": ["изен"]},
            khakas_russian={
                "завершать": ["тоозарға", "тӱгедерге"],
                "кто": ["кем"],
                "я": ["мин", "мағаа", "минің"],
                "снег": ["хар", "чаас"],
            },
            explanatory={},
            literary={},
        )
        complete = rg.review_row(
            {"en": "complete", "ru_from_en_by_google": "полный", "kjh_from_ru_by_yandex": "толдыра"},
            indexes,
        )
        self.assertEqual(complete["ru_corrected"], "завершать")
        self.assertEqual(complete["kjh_corrected"], "тоозарға; тӱгедерге")
        self.assertEqual(complete["review_status"], "confirmed")

        who = rg.review_row(
            {"en": "who", "ru_from_en_by_google": "ВОЗ", "kjh_from_ru_by_yandex": "ВОЗ"},
            indexes,
        )
        self.assertEqual((who["ru_corrected"], who["kjh_corrected"]), ("кто", "кем"))

        pronoun = rg.review_row(
            {"en": "I", "ru_from_en_by_google": "я", "kjh_from_ru_by_yandex": "мин"},
            indexes,
        )
        self.assertEqual(pronoun["kjh_corrected"], "мин")

        hello = rg.review_row(
            {"en": "Hello", "ru_from_en_by_google": "Привет", "kjh_from_ru_by_yandex": "Изен"},
            indexes,
        )
        self.assertEqual(hello["kjh_corrected"], "изен")

        snow = rg.review_row(
            {"en": "snow", "ru_from_en_by_google": "снег", "kjh_from_ru_by_yandex": ""},
            indexes,
        )
        self.assertEqual(snow["kjh_corrected"], "хар; чаас")

        ewe = rg.review_row(
            {"en": "Ewe", "ru_from_en_by_google": "Овца", "kjh_from_ru_by_yandex": "Хой"},
            indexes,
        )
        self.assertEqual(ewe["ru_corrected"], "эве")
        self.assertEqual(ewe["kjh_corrected"], "")
        self.assertEqual(ewe["review_status"], "missing")
        self.assertIn("missing_after_ru_correction", ewe["review_flags"])

        for english, russian in {
            "a": "неопределённый артикль",
            "the": "определённый артикль",
            "TRUE": "истина",
            "FALSE": "ложь",
            "great": "отличный",
            "will": "будет",
            "hard": "трудный",
            "call": "звонить",
            "offer": "предлагать",
            "free": "свободный",
            "set": "устанавливать",
            "cool": "классный",
        }.items():
            result = rg.review_row(
                {"en": english, "ru_from_en_by_google": "старое значение", "kjh_from_ru_by_yandex": "старый перевод"},
                indexes,
            )
            self.assertEqual(result["ru_corrected"], russian)

    def test_yandex_is_retained_only_when_russian_meaning_did_not_change(self):
        indexes = rg.SourceIndexes({}, {}, {}, {})
        unchanged = rg.review_row(
            {"en": "future", "ru_from_en_by_google": "будущее", "kjh_from_ru_by_yandex": "килҷең тус"},
            indexes,
        )
        self.assertEqual(unchanged["kjh_corrected"], "килҷең тус")
        self.assertEqual(unchanged["review_status"], "unverified_yandex")

        changed = rg.review_row(
            {"en": "language-name", "ru_from_en_by_google": "животное", "kjh_from_ru_by_yandex": "мал"},
            indexes,
            ru_overrides={"language-name": "название языка"},
        )
        self.assertEqual(changed["kjh_corrected"], "")
        self.assertEqual(changed["review_status"], "missing")

    def test_yandex_disambiguates_explanatory_only_candidates(self):
        indexes = rg.SourceIndexes(
            base={},
            khakas_russian={},
            explanatory={"ходить": ["постирға", "чӧрерге", "хастирға"]},
            literary={},
        )
        result = rg.review_row(
            {"en": "walk", "ru_from_en_by_google": "ходить", "kjh_from_ru_by_yandex": "чӧрерге"},
            indexes,
        )
        self.assertEqual(result["kjh_corrected"], "чӧрерге")
        self.assertEqual(result["kjh_sources"], "khakas-explanatory-dict")
        self.assertEqual(result["review_status"], "confirmed")

    def test_explanatory_definitions_are_not_mistaken_for_synonyms(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = {
                "base": root / "base.csv",
                "khakas_russian": root / "kr.csv",
                "explanatory": root / "ex.csv",
                "literary": root / "lit.csv",
            }
            self._write(paths["base"], [["ru", "kjh"]])
            self._write(paths["khakas_russian"], [["word", "semgloss", "field1"]])
            self._write(paths["explanatory"], [
                ["headword_fix", "field_fix"],
                ["КІЗІ", "**КІЗІ** -- Человек."],
                ["ААЛҶЫ", "**ААЛҶЫ** -- Человек, прибывший в гости из другого села."],
                ["ТООЗАРҒА [тоос-]", "**ТООЗАРҒА** -- Кончать, заканчивать, приводить к концу."],
            ])
            self._write(paths["literary"], [
                ["headword_fix", "field_fix"],
                ["РОМАН", "**РОМАН** -- Эпический жанр."],
            ])

            indexes = rg.build_source_indexes(paths)

            self.assertEqual(indexes.explanatory["человек"], ["кізі"])
            self.assertNotIn("аалҷы", indexes.explanatory["человек"])
            self.assertEqual(indexes.explanatory["заканчивать"], ["тоозарға"])
            self.assertEqual(indexes.literary, {})

    def test_end_to_end_preserves_source_columns_and_row_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            main = root / "main.csv"
            output = root / "out.csv"
            dictionaries = {
                "base": root / "base.csv",
                "khakas_russian": root / "kr.csv",
                "explanatory": root / "ex.csv",
                "literary": root / "lit.csv",
            }
            self._write(main, [
                ["en", "ru_from_en_by_google", "kjh_from_ru_by_yandex"],
                ["Hello", "Привет", "Изен"],
                ["Ewe", "Овца", "Хой"],
            ])
            self._write(dictionaries["base"], [["ru", "kjh"], ["привет", "изен"]])
            self._write(dictionaries["khakas_russian"], [["word", "semgloss", "field1"], ["кем", "кто", ""]])
            self._write(dictionaries["explanatory"], [["headword_fix", "field_fix"]])
            self._write(dictionaries["literary"], [["headword_fix", "field_fix"]])

            rg.build_reviewed_csv(main, dictionaries, output)

            with main.open(encoding="utf-8", newline="") as handle:
                source = list(csv.DictReader(handle))
            with output.open(encoding="utf-8", newline="") as handle:
                reviewed = list(csv.DictReader(handle))
            self.assertEqual(len(reviewed), 2)
            for original, result in zip(source, reviewed):
                for column in rg.INPUT_COLUMNS:
                    self.assertEqual(result[column], original[column])
            self.assertEqual(list(reviewed[0]), rg.OUTPUT_COLUMNS)

    def test_validation_rejects_duplicate_variants_and_changed_source_data(self):
        source = [{"en": "Hello", "ru_from_en_by_google": "Привет", "kjh_from_ru_by_yandex": "Изен"}]
        reviewed = [{
            **source[0],
            "en": "Changed",
            "ru_corrected": "Привет",
            "kjh_corrected": "изен; Изен",
            "kjh_sources": "khakas-russian-dict",
            "review_status": "confirmed",
            "review_flags": "multiple_kjh",
            "review_note": "",
        }]
        errors = rg.validate_reviewed_rows(source, reviewed, expected_count=1)
        self.assertTrue(any("source column" in error for error in errors))
        self.assertTrue(any("duplicate Khakas variant" in error for error in errors))

    @staticmethod
    def _write(path, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerows(rows)

    def _manual_review_module(self):
        self.assertIsNotNone(
            importlib.util.find_spec("manual_review"),
            "manual_review.py must provide the interactive review feature",
        )
        return importlib.import_module("manual_review")

    @staticmethod
    def _reviewed_stub(english, russian, khakas):
        return {
            "en": english,
            "ru_from_en_by_google": russian,
            "kjh_from_ru_by_yandex": khakas,
            "ru_corrected": russian,
            "kjh_corrected": khakas,
            "kjh_sources": "khakas-russian-dict",
            "function_word_handling": "not_applicable",
            "frequent_kjh": "",
            "native_review": "none",
            "review_status": "confirmed",
            "review_flags": "",
            "review_note": "",
        }


if __name__ == "__main__":
    unittest.main()
