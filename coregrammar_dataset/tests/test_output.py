import csv
import json
import tempfile
import unittest
from pathlib import Path

from coregrammar_dataset.coregrammar.models import Candidate, SelectedRecord
from coregrammar_dataset.coregrammar.output import OUTPUT_FIELDS, split_sentences_csv, write_outputs


class OutputTests(unittest.TestCase):
    def test_splits_csv_into_exact_stratified_chunks_without_losing_rows(self):
        rows = []
        strata = [
            ("tatoeba", "simple_clause", 5),
            ("tatoeba", "question", 3),
            ("common_voice", "simple_clause", 4),
        ]
        index = 1
        for source, construction, count in strata:
            for _ in range(count):
                rows.append({
                    "id": f"cg-{index:06d}",
                    "ru": f"Предложение {index}.",
                    "source": source,
                    "primary_construction": construction,
                })
                index += 1

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_csv = root / "sentences.csv"
            with source_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=("id", "ru", "source", "primary_construction"),
                )
                writer.writeheader()
                writer.writerows(rows)

            output = root / "sentences_3"
            paths = split_sentences_csv(source_csv, output, chunk_size=4)

            self.assertEqual(
                ["sentences_001.csv", "sentences_002.csv", "sentences_003.csv"],
                [path.name for path in paths],
            )
            chunks = []
            for path in paths:
                with path.open(encoding="utf-8", newline="") as handle:
                    chunk = list(csv.DictReader(handle))
                    self.assertEqual(
                        ["id", "ru", "source", "primary_construction"],
                        list(chunk[0]),
                    )
                    self.assertEqual(4, len(chunk))
                    chunks.append(chunk)

            all_rows = [row for chunk in chunks for row in chunk]
            self.assertEqual(
                {row["id"] for row in rows},
                {row["id"] for row in all_rows},
            )
            self.assertEqual(len(rows), len({row["id"] for row in all_rows}))

            expected_totals = {
                ("tatoeba", "simple_clause"): 5,
                ("tatoeba", "question"): 3,
                ("common_voice", "simple_clause"): 4,
            }
            for stratum, total in expected_totals.items():
                per_chunk = [
                    sum(
                        (row["source"], row["primary_construction"]) == stratum
                        for row in chunk
                    )
                    for chunk in chunks
                ]
                self.assertLessEqual(max(per_chunk) - min(per_chunk), 1)
                self.assertEqual(total, sum(per_chunk))

    def test_split_refuses_existing_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_csv = root / "sentences.csv"
            source_csv.write_text(
                "id,source,primary_construction\n1,tatoeba,question\n",
                encoding="utf-8",
            )
            output = root / "sentences_1"
            output.mkdir()
            with self.assertRaises(FileExistsError):
                split_sentences_csv(source_csv, output, chunk_size=1)

    def test_writes_complete_artifact_set(self):
        candidate = Candidate(
            ru="Мне нужно купить свежий хлеб.",
            source="massive",
            source_id="m-1",
            source_url="https://example.test/1",
            license="CC BY 4.0",
            domain="shopping",
            metadata={"intent": "shopping_list"},
            construction_labels=("possession_modality_impersonal",),
        )
        record = SelectedRecord(candidate, "possession_modality_impersonal")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "result"
            write_outputs(
                output,
                records=[record],
                reserve=[record],
                quota_rows=[{"dimension": "source", "name": "massive", "requested": 1, "actual": 1}],
                rejected=[{"ru": "http://bad", "source": "test", "reason": "url"}],
                near_duplicates=[],
                manifest={"requested_total": 1, "seed": 42},
            )
            expected = {
                "sentences.csv", "sentences.jsonl", "reserve.csv", "quota_report.csv",
                "rejected.csv", "near_duplicates.csv", "manifest.json", "README.md",
            }
            self.assertEqual(expected, {p.name for p in output.iterdir()})
            with (output / "sentences.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(list(OUTPUT_FIELDS), list(rows[0]))
            self.assertEqual("", rows[0]["kjh"])
            self.assertEqual("train", rows[0]["split"])
            self.assertEqual("pending", rows[0]["translation_status"])
            self.assertEqual(["possession_modality_impersonal"], json.loads(rows[0]["construction_labels"]))
            self.assertEqual(1, len((output / "sentences.jsonl").read_text(encoding="utf-8").splitlines()))

    def test_refuses_existing_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "result"
            output.mkdir()
            with self.assertRaises(FileExistsError):
                write_outputs(output, [], [], [], [], [], {})


if __name__ == "__main__":
    unittest.main()
