"""Ingestion configuration (Spec 004 R12).

`IngestionConfig` is the versioned, index-defining file `config/ingestion.yaml`.
`RuntimeSettings` holds environment-specific values; the API key is a secret and
never appears in reprs, messages or the run summary.
"""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    ValidationError,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from way2australia_rag.ingestion.errors import IngestionConfigurationError

DEFAULT_CONFIG_PATH = "config/ingestion.yaml"
_FLOATING_REVISIONS = frozenset({"main", "latest"})


class EmbedderConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    provider: Literal["bge_m3", "fake"]
    model_id: str
    revision: str
    batch_size: int = Field(ge=1)
    normalize: bool
    fake_vector_size: int = Field(ge=1)


class ChunkerConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    version: str
    max_chunk_chars: int = Field(ge=16)


class IngestionConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1.0"]
    index_version: str = Field(min_length=1)
    embedder: EmbedderConfig
    chunker: ChunkerConfig


def load_ingestion_config(path: Path) -> IngestionConfig:
    """Load and validate the config file; any problem is a configuration error."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        # Only the file name: never the absolute path or parser excerpts.
        raise IngestionConfigurationError(
            f"cannot read ingestion config '{path.name}' ({type(error).__name__})"
        ) from None
    if not isinstance(raw, dict):
        raise IngestionConfigurationError(
            f"ingestion config '{path.name}' must be a YAML mapping"
        )
    try:
        config = IngestionConfig.model_validate(raw)
    except ValidationError as error:
        fields = sorted({".".join(str(p) for p in e["loc"]) for e in error.errors()})
        raise IngestionConfigurationError(
            f"invalid ingestion config '{path.name}': check {', '.join(fields)}"
        ) from None
    revision = config.embedder.revision.strip()
    if not revision or revision.lower() in _FLOATING_REVISIONS:
        raise IngestionConfigurationError(
            "embedder.revision must be a pinned full commit SHA; "
            "a missing revision, 'main' or 'latest' is refused."
        )
    return config


class RuntimeSettings(BaseSettings):
    """Environment-specific settings (environment and `.env`, never committed)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    qdrant_url: str = Field(
        default="http://localhost:6333", validation_alias="QDRANT_URL"
    )
    qdrant_api_key: SecretStr | None = Field(
        default=None, validation_alias="QDRANT_API_KEY"
    )
    collection_base: str = Field(
        default="way2australia", validation_alias="QDRANT_COLLECTION_BASE"
    )
    tenant_id: str = Field(default="way2australia", validation_alias="W2A_TENANT_ID")
    # Directory of the derived lexical index files (Spec 007 R4). None means the
    # default `<repo-root>/.local/lexical`. Not index-defining.
    lexical_index_dir: Path | None = Field(
        default=None, validation_alias="W2A_LEXICAL_INDEX_DIR"
    )

    @field_validator("lexical_index_dir", mode="before")
    @classmethod
    def _blank_lexical_dir_is_default(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("tenant_id")
    @classmethod
    def _tenant_not_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("W2A_TENANT_ID must not be empty")
        return value


def load_runtime_settings(
    error_type: type[Exception] = IngestionConfigurationError,
) -> RuntimeSettings:
    """The one place `RuntimeSettings` is built for the CLIs (Spec 005 R1).

    A validation failure becomes `error_type` naming only environment variable
    names, never their values.
    """
    try:
        return RuntimeSettings()
    except ValidationError as error:
        aliases = {
            name: str(field.validation_alias or name)
            for name, field in RuntimeSettings.model_fields.items()
        }
        names = sorted(
            {
                aliases.get(str(e["loc"][0]), str(e["loc"][0]))
                for e in error.errors()
                if e["loc"]
            }
        )
        if not names:  # e.g. a model-level error with no field location
            raise error_type("invalid runtime settings.") from None
        raise error_type(
            f"invalid runtime settings: check {', '.join(names)}."
        ) from None
