"""Generator interface, identity and usage (Spec 012 R4)."""

from typing import TYPE_CHECKING, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from way2australia_rag.generation.prompts import RenderedPrompt


class GeneratorInfo(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    provider: Literal["bedrock", "fake"]
    model_id: str
    model_id_source: Literal["config", "cli", "env"]
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


class GeneratorOutput(BaseModel):
    """Parsed structured output plus usage; citations are validated later."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    answerable: bool
    answer: str
    citations: list[str]
    usage: GeneratorUsage
    stop_reason: str | None = None


class Generator(Protocol):
    info: GeneratorInfo

    def generate(self, prompt: "RenderedPrompt") -> GeneratorOutput: ...

    def close(self) -> None: ...
