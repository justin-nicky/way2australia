"""One JSON log line per answer request (Spec 013 R13, D-L).

Never logged: query text or hash, answer or evidence text, configured URLs,
keys, client exception messages (error lines carry the class name only).
"""

import json
import logging
from typing import Any

from way2australia_rag.generation.models import AnswerResponse

LOGGER_NAME = "way2australia_api.answer"
answer_logger = logging.getLogger(LOGGER_NAME)


def configure_logging() -> None:
    for name in ("httpx", "anthropic"):
        logging.getLogger(name).setLevel(logging.WARNING)
    answer_logger.setLevel(logging.INFO)
    if not logging.getLogger().handlers and not answer_logger.handlers:
        answer_logger.addHandler(logging.StreamHandler())


def rerank_label(record: dict[str, Any] | None) -> str:
    if record is None:
        return "off"
    if record.get("skipped_reason"):
        return f"skipped:{record['skipped_reason']}:{record.get('stage')}"
    return "applied"


def build_log_record(
    *,
    request_id: str,
    response: AnswerResponse,
    breaker: str | None,
    generator_provider: str | None,
    generator_model: str | None,
    fake: bool,
    query_chars: int,
    script_mix: str,
    abandoned_in_flight: int,
) -> dict[str, Any]:
    retrieval = response.identity.retrieval
    latency = response.latency_ms
    return {
        "event": "answer",
        "request_id": request_id,
        "status": response.status.value,
        "reason": response.reason.value if response.reason else None,
        "sub_reason": response.sub_reason,
        "served_strategy": retrieval.get("strategy"),
        "fallback_reason": retrieval.get("fallback_reason"),
        "rerank": rerank_label(retrieval.get("rerank")),
        "breaker": breaker,
        "generator": {"provider": generator_provider, "model_id": generator_model},
        "fake": fake,
        "latency_ms": {
            "retrieval": latency.get("retrieval_ms"),
            "context": latency.get("context_ms"),
            "generation": latency.get("generation_ms"),
            "total": latency.get("total_ms"),
        },
        "query_chars": query_chars,
        "script_mix": script_mix,
        "abandoned_in_flight": abandoned_in_flight,
    }


def log_answer(record: dict[str, Any]) -> None:
    answer_logger.info(json.dumps(record, sort_keys=True, default=str))
