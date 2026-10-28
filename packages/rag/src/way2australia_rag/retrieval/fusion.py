"""Reciprocal rank fusion (Spec 007 R7, R8).

`rrf_fuse` is pure: no I/O, no authorization logic. It accepts only
`RetrievedChunk`s that a retriever has already filtered and re-checked
(`check_hit`), so nothing unauthorized can reach it (D040).
"""

from collections.abc import Mapping, Sequence
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictFloat,
    StrictInt,
    field_validator,
)

from way2australia_rag.retrieval.base import MAX_TOP_K, MIN_TOP_K
from way2australia_rag.retrieval.models import RetrievedChunk

LEGS: tuple[str, str] = ("dense", "bm25")

# Strict: `true` and quoted numbers are configuration errors, not coerced.
PositiveWeight = Annotated[StrictInt | StrictFloat, Field(gt=0, allow_inf_nan=False)]


class FusionConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    method: Literal["rrf"]
    k: StrictInt = Field(ge=1)
    weights: dict[str, PositiveWeight]
    candidate_depth: StrictInt = Field(ge=MIN_TOP_K, le=MAX_TOP_K)

    @field_validator("weights")
    @classmethod
    def _weights_cover_exactly_the_legs(
        cls, value: dict[str, float]
    ) -> dict[str, float]:
        if set(value) != set(LEGS):
            raise ValueError(f"weights must have exactly the keys {', '.join(LEGS)}")
        return value


class FusedHit(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    chunk: RetrievedChunk
    score: float
    leg_ranks: dict[str, int | None]


def rrf_fuse(
    legs: Mapping[str, Sequence[RetrievedChunk]],
    k: int,
    weights: Mapping[str, float],
) -> list[FusedHit]:
    """Fuse ranked legs: `fused = sum(weights[leg] / (k + rank))`.

    Order is `(-fused, best_rank, point_id)`. The chunk copy kept is the first
    seen in `legs` iteration order (callers put the dense leg first). A leg
    that lists a point twice counts only its best (first) rank. Each hit's
    `leg_ranks` has one entry per leg, `None` where the leg did not return it.
    """
    chunks: dict[str, RetrievedChunk] = {}
    ranks: dict[str, dict[str, int]] = {}
    for leg, hits in legs.items():
        for position, hit in enumerate(hits, start=1):
            per_leg = ranks.setdefault(hit.point_id, {})
            if leg in per_leg:
                continue
            per_leg[leg] = position
            chunks.setdefault(hit.point_id, hit)
    fused: list[tuple[float, int, str]] = []
    for point_id, per_leg in ranks.items():
        score = sum(weights[leg] / (k + rank) for leg, rank in per_leg.items())
        fused.append((score, min(per_leg.values()), point_id))
    fused.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [
        FusedHit(
            chunk=chunks[point_id],
            score=score,
            leg_ranks={leg: ranks[point_id].get(leg) for leg in legs},
        )
        for score, _, point_id in fused
    ]
