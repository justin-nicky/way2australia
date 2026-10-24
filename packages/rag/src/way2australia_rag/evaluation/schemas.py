"""Local JSON Schema registry for evaluation assets (Spec 006 R2).

The three schema files under `evaluation/schemas/` are registered by their
`$id`, so `$ref` between them resolves locally. Nothing is fetched over the
network and nothing is written.
"""

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from way2australia_rag.evaluation.errors import EvaluationConfigurationError

SCHEMA_DIR = "evaluation/schemas"
CASE_SCHEMA = "evaluation_case.schema.json"
SUITE_SCHEMA = "evaluation_suite.schema.json"
CASE_TYPES_SCHEMA = "evaluation_case_types.schema.json"
SCHEMA_FILES = (CASE_SCHEMA, SUITE_SCHEMA, CASE_TYPES_SCHEMA)


class EvaluationSchemas:
    """The registry plus validators for the suite, each case type and candidates."""

    def __init__(self, registry: Registry) -> None:  # type: ignore[type-arg]
        self._registry = registry

    def _validator(self, ref: str) -> Draft202012Validator:
        return Draft202012Validator({"$ref": ref}, registry=self._registry)

    def suite(self) -> Draft202012Validator:
        return self._validator(SUITE_SCHEMA)

    def case_type(self, name: str) -> Draft202012Validator:
        return self._validator(f"{CASE_TYPES_SCHEMA}#/$defs/{name}")

    def candidate_row(self) -> Draft202012Validator:
        return self.case_type("candidate_row")


def load_schemas(repo_root: Path) -> EvaluationSchemas:
    """Build the local registry; a missing or invalid schema is a config error."""
    registry: Registry = Registry()  # type: ignore[type-arg]
    for name in SCHEMA_FILES:
        path = repo_root / SCHEMA_DIR / name
        try:
            contents = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(contents)
        except (OSError, ValueError) as error:
            raise EvaluationConfigurationError(
                f"cannot read schema '{name}' as JSON."
            ) from error
        except Exception as error:  # jsonschema.SchemaError
            raise EvaluationConfigurationError(
                f"schema '{name}' is not a valid Draft 2020-12 schema."
            ) from error
        schema_id = contents.get("$id") if isinstance(contents, dict) else None
        if schema_id != name:
            raise EvaluationConfigurationError(
                f"schema '{name}' must declare $id '{name}'."
            )
        registry = registry.with_resource(
            name, Resource.from_contents(contents, DRAFT202012)
        )
    return EvaluationSchemas(registry)
