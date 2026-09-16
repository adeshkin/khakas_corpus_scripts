# CoreGrammar Dataset Preparation Design

## Goal

Create a reproducible Python utility that downloads Russian sentence sources, filters and classifies their sentences, and selects a requested number of records according to configurable source and grammatical-construction percentages. The resulting corpus is intended for human translation into Khakas and later training of a low-resource Russian-to-Khakas machine-translation model, with extra weight on constructions that should not be copied literally from Russian.

## Location and scope

All new implementation files live under `external_datasets/coregrammar/` in the existing `khakas_corpus_scripts` repository. Existing one-off utilities remain unchanged. The current user modification in `smol/smoldoc/download.py` is out of scope.

The utility prepares Russian source sentences only. It does not translate them, train a model, or upload a dataset to Hugging Face.

## User interface

The primary entry point is:

```bash
python external_datasets/coregrammar/prepare_coregrammar.py \
  --total 3000 \
  --seed 42 \
  --output external_datasets/coregrammar/output/coregrammar_3000
```

Additional options:

- `--config PATH`: YAML configuration override.
- `--cache-dir PATH`: downloaded dataset cache.
- `--strict-quotas`: fail instead of redistributing an unfillable quota.
- `--sources NAME ...`: restrict the enabled source adapters.
- `--offline`: use only cached or local data.

## Default source allocation

| Source | Share | Preferred access | Fallback |
|---|---:|---|---|
| Tatoeba Russian | 45% | Hugging Face-compatible mirror when configured | Official Tatoeba exports |
| Mozilla Common Voice Russian sentence inventory | 30% | Hugging Face dataset when access is available | Mozilla Data Collective/local TSV |
| UD Russian Taiga | 15% | Hugging Face/Universal Dependencies dataset | Official GitHub CoNLL-U files |
| Amazon MASSIVE `ru-RU` | 10% | `AmazonScience/massive` on Hugging Face | None; quota is redistributed in non-strict mode |

The exact dataset identifiers and revisions are configuration values rather than hard-coded assumptions. Download failures include an actionable message explaining the fallback or required authentication.

## Default construction allocation

Construction quotas are global rather than independently repeated for every source:

| Construction | Share | Purpose |
|---|---:|---|
| `simple_clause` | 25% | Core argument structure and target-final predicate practice |
| `question_negation_imperative` | 15% | Frequent household interaction patterns |
| `relative_attributive` | 15% | Russian `который/где/куда/откуда`; Khakas participial restructuring |
| `temporal_aspectual` | 12% | `когда/пока/после того как`, action sequencing |
| `possession_modality_impersonal` | 10% | `у меня есть`, `мне нужно`, `можно/нельзя` |
| `motion_location` | 10% | Direction, location, source and goal marking |
| `condition_purpose_cause` | 8% | `если/чтобы/потому что/хотя` |
| `dialogue_ellipsis` | 5% | Short natural replies and incomplete conversational turns |

Classification is deterministic and multi-label. Selection assigns each sentence to one primary quota using a rarest-needed-first algorithm, while retaining all detected labels in the output.

## Filtering and normalization

Candidates are normalized with Unicode NFC and whitespace cleanup without changing their displayed wording. A separate comparison key lowercases text, maps `ё` to `е`, normalizes punctuation and collapses whitespace for duplicate detection.

Default quality rules:

- 4–20 word-like tokens;
- predominantly Cyrillic Russian text;
- no URLs, email addresses, HTML, unresolved markup or control characters;
- no duplicate normalized sentences across sources;
- no sentences consisting mainly of names, numbers or punctuation;
- source-specific filtering, including original-Russian preference for Tatoeba and exclusion of Taiga poetry where metadata permits;
- no automatic rewriting of source sentences.

Rejected-candidate counts and reasons are recorded in the manifest.

## Quota allocation

Percentage values must be non-negative and sum to 100 within a small floating-point tolerance. Integer targets use the largest-remainder method so every requested row is assigned exactly once.

Selection occurs in two constraints:

1. Allocate exact source targets.
2. Within the remaining candidate pool, satisfy global construction deficits using rarest-needed-first selection with deterministic seeded tie-breaking.

If the exact cross-constraint solution is impossible, default mode redistributes only the unavailable portion and records the difference. `--strict-quotas` exits non-zero with a table of deficits.

## Data splits

The default split allocation is:

- train: 90%;
- validation: 5%;
- test: 5%.

Splitting is stratified by primary construction and source as far as integer counts allow. The seed controls candidate shuffling, quota tie-breaking and split assignment.

## Outputs

The output directory contains:

- `sentences.jsonl`: canonical machine-readable result;
- `sentences.csv`: spreadsheet-friendly equivalent;
- `manifest.json`: configuration, seed, source identifiers/revisions, licenses, download mode, filter statistics and hashes;
- `quota_report.csv`: requested and actual counts by source, construction and split;
- `README.md`: generated summary and attribution notes.

Each selected row contains:

```json
{
  "id": "coregrammar_000001",
  "ru": "...",
  "kjh": "",
  "source": "tatoeba",
  "source_id": "...",
  "source_url": "...",
  "license": "...",
  "primary_construction": "relative_attributive",
  "construction_labels": ["relative_attributive", "temporal_aspectual"],
  "domain": "unknown",
  "original_language": "ru",
  "split": "train",
  "translation_status": "pending"
}
```

## Components

- `prepare_coregrammar.py`: CLI orchestration and user-facing errors.
- `coregrammar/config.py`: defaults, YAML loading and percentage validation.
- `coregrammar/models.py`: typed candidate and selected-record structures.
- `coregrammar/sources.py`: source adapters and fallback handling.
- `coregrammar/filtering.py`: normalization, quality checks and deduplication.
- `coregrammar/classification.py`: deterministic construction rules.
- `coregrammar/selection.py`: integer quotas, constrained selection and splitting.
- `coregrammar/output.py`: JSONL/CSV/manifest/report writers.
- `config.default.yaml`: editable default distributions and dataset identifiers.
- `tests/fixtures/`: small local samples representing every source format.

## Dependencies

Production dependencies are kept small: `datasets`, `huggingface_hub`, `PyYAML`, `requests`, `conllu`, and the repository's existing `razdel`. Tests use `pytest`. Dataset loading is isolated behind adapters so selection and classification tests never require network access.

## Error handling

- Configuration errors fail before downloading anything.
- A failed source reports its attempted endpoints and fallback status.
- Non-strict mode may continue only when remaining sources can fill the total.
- An insufficient global candidate pool always fails with requested/available counts.
- Output is written to a temporary sibling directory and renamed only after every file is complete, preventing half-written deliverables.

## Testing strategy

Development follows test-driven development. Offline tests cover percentage validation, largest-remainder rounding, normalization, filtering, duplicate removal, construction classification, deterministic selection, quota redistribution, strict failures, stratified splitting, source-format parsing and output schemas. A separate opt-in smoke test exercises live downloads without being part of the default test suite.

## Acceptance criteria

For `--total 3000 --seed 42`, given sufficient source candidates, the utility produces exactly 3,000 unique rows, identical across repeated runs against pinned source revisions. Requested and actual source/construction/split counts are visible in the reports. Every record is attributable to a source and license, contains an empty Khakas translation field, and is ready for spreadsheet or JSONL translation workflows.
