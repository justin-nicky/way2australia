"""Generation configuration (Spec 012).

T1 defines only the context budget. The full `GenerationConfig` loader for
`config/generation.yaml` is completed in T3.
"""

from pydantic import BaseModel, ConfigDict, Field


class ContextConfig(BaseModel):
    """Evidence budget: block count and total evidence characters."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    max_blocks: int = Field(ge=1)
    max_chars: int = Field(ge=1)
