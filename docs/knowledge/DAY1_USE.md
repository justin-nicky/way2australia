# Day-1 usage

Start with these production-truth sources:
- `knowledge/public/business/`
- `knowledge/public/official/`
- `knowledge/public/languages/ml/`

Use:
- `knowledge/manifest/document_manifest.jsonl` for ingestion;
- `evaluation/datasets/golden_public.jsonl` for initial retrieval evaluation;
- `evaluation/datasets/unanswerable_public.jsonl` after generation/refusal is implemented;
- `evaluation/datasets/security_public.jsonl` only in the security test harness.

Do **not** index `tests/fixtures/security/` into the normal production collection.
Create a dedicated test collection/corpus for them.

Initial experiment:
`experiments/configs/day1_baseline.yaml`

The owner-approved FAQ pairs are also preserved in structured form at:
`knowledge/structured/owner_approved_faq_pairs.jsonl`.
