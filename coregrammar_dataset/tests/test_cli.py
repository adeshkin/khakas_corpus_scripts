import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "coregrammar_dataset" / "prepare_coregrammar.py"
SPLIT_SCRIPT = ROOT / "coregrammar_dataset" / "split_sentences.py"
FIXTURES = Path(__file__).parent / "fixtures"


class CliTests(unittest.TestCase):
    def test_split_cli_creates_numbered_csv_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_csv = root / "sentences.csv"
            source_csv.write_text(
                "id,source,primary_construction\n"
                "1,tatoeba,question\n"
                "2,tatoeba,question\n"
                "3,common_voice,simple_clause\n"
                "4,common_voice,simple_clause\n",
                encoding="utf-8",
            )
            output = root / "sentences_2"
            result = subprocess.run(
                [sys.executable, str(SPLIT_SCRIPT), str(source_csv),
                 "--output", str(output), "--chunk-size", "2"],
                cwd=ROOT, text=True, capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(
                ["sentences_001.csv", "sentences_002.csv"],
                sorted(path.name for path in output.iterdir()),
            )

    def test_invalid_total_is_rejected_before_config_access(self):
        for total in (0, 100001):
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--total", str(total), "--output", "/unused",
                 "--config", "/definitely/missing.yaml"], text=True, capture_output=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("--total must be between 1 and 100000", result.stderr)
            self.assertNotIn("missing.yaml", result.stderr)

    def test_offline_fixture_run_writes_exact_total(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "fixture.yaml"
            config.write_text(
                "sources:\n"
                "  tatoeba:\n"
                "    percentage: 100\n"
                f"    local_path: {json.dumps(str(FIXTURES / 'tatoeba.tsv'))}\n"
                "  common_voice:\n    enabled: false\n"
                "  massive:\n    enabled: false\n"
                "blocklists: []\n",
                encoding="utf-8",
            )
            output = root / "out"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--total", "1", "--seed", "7",
                 "--output", str(output), "--cache-dir", str(root / "cache"),
                 "--config", str(config), "--offline"],
                cwd=ROOT, text=True, capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            with (output / "sentences.csv").open(encoding="utf-8", newline="") as handle:
                self.assertEqual(1, len(list(csv.DictReader(handle))))
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(1, manifest["actual_total"])


if __name__ == "__main__":
    unittest.main()
