"""Generator identity and usage (Spec 012 R4).

The `Generator` Protocol and adapter implementations are added in T3.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class GeneratorInfo(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    provider: Literal["bedrock", "fake"]
    model_id: str
    endpoint: str | None
    region: str | None
    inference_profile: str | None
    effort: str | None
    max_tokens: int
    request_timeout_s: float
    retries: int
    deadline_s: float
    is_fake: bool


class GeneratorUsage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    input_tokens: int | None = None
    output_tokens: int | None = None
    attempts: int = Field(ge=1)
