# Way2Australia RAG Seed v3

This is the Phase-1 seed knowledge/evaluation package aligned with the latest plan.

## Structure

```text
knowledge/
  public/
    business/
    official/
    languages/ml/
  structured/
  manifest/
  schemas/
  releases/

sources/
  raw/

evaluation/
  datasets/
  suites/
  schemas/
  retrieval/
  generation/
  security/
  metrics/

tests/
  fixtures/security/

config/

experiments/
  configs/
  results/

analytics/
  schemas/

docs/
```

## New versioning concepts

- Knowledge documents have stable `document_id` + `document_version`.
- Evaluation cases have stable `case_id` + `case_version` + lifecycle `status`.
- `knowledge/releases/seed-v1.json` is the initial lightweight Knowledge Release.
- `evaluation/suites/public-eval-v1.json` defines the evaluation cases attached to that release.
- Chunks/indexes are derived artifacts and are not the source of truth.
- `DocumentRepository` is implemented in application code, not in this seed package. Phase 1 uses local files; Phase 2 can use S3 without changing the RAG pipeline contract.

## Normal Day-1 corpus

Index only:

- `knowledge/public/business/`
- `knowledge/public/official/`
- `knowledge/public/languages/ml/`

Do not index raw sources, docs, evaluation datasets, security fixtures, experiment files, analytics schemas, or release manifests.
