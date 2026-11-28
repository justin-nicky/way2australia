"""POST /v1/answer (Spec 013 R9-R13). A sync handler: FastAPI runs it on the
threadpool, so retrieval and generation never block the event loop."""

import logging
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from way2australia_rag.retrieval.access import guest_access, resolve_access
from way2australia_rag.retrieval.applicability import resolve_lote
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.script_mix import script_mix
from way2australia_rag.serving.readiness import Phase
from way2australia_rag.serving.stack import ServingNotReadyError

from way2australia_api.contract import AnswerContract, AnswerRequest, to_contract
from way2australia_api.errors import error_response, request_id_of
from way2australia_api.logs import build_log_record, log_answer
from way2australia_api.middleware import fake_headers

router = APIRouter(tags=["answer"])
logger = logging.getLogger(__name__)


def _invalid(request: Request, loc: str, msg: str) -> JSONResponse:
    return error_response(
        request, 422, "invalid_request", fields=[{"loc": ["body", loc], "msg": msg}]
    )


@router.post("/v1/answer", response_model=AnswerContract)
def post_answer(body: AnswerRequest, request: Request) -> JSONResponse:
    state = request.app.state
    serving = state.serving_config
    loader = getattr(state, "loader", None)
    holder = loader.holder if loader is not None else None
    if state.readiness.phase is not Phase.READY or holder is None:
        return error_response(
            request,
            503,
            "not_ready",
            headers={"Retry-After": str(serving.concurrency.retry_after_not_ready_s)},
        )
    pool = state.slots
    slot = pool.try_acquire()
    if slot is None:
        return error_response(
            request,
            503,
            "busy",
            headers={"Retry-After": str(serving.concurrency.retry_after_busy_s)},
        )
    try:
        query = body.query.strip()
        if not query:
            return _invalid(request, "query", "query must not be empty")
        if len(query) > serving.request.max_query_chars:
            return _invalid(
                request,
                "query",
                f"query must be at most {serving.request.max_query_chars} characters",
            )
        try:
            lote = resolve_lote(body.lote, state.lote_codes)
        except RetrievalConfigurationError:
            codes = ", ".join(sorted(state.lote_codes))
            return _invalid(request, "lote", f"lote must be one of: {codes}")
        access = resolve_access(guest_access(state.runtime_settings))
        with holder.acquire() as stack:
            response = stack.service.answer(
                query,
                access,
                top_k=state.top_k,
                lote=lote,
                budget_s=serving.budget.request_s,
                min_generation_s=serving.budget.min_generation_s,
                on_abandoned=slot.transfer,
            )
        request_id = request_id_of(request) or ""
        contract = to_contract(response, request_id)
        info = holder.generator.info if holder.generator is not None else None
        breaker = holder.breaker
        record: dict[str, Any] = build_log_record(
            request_id=request_id,
            response=response,
            breaker=breaker.state.value if breaker is not None else None,
            generator_provider=info.provider if info else None,
            generator_model=info.model_id if info else None,
            fake=state.settings.api_fake,
            query_chars=len(query),
            script_mix=script_mix(query),
            abandoned_in_flight=pool.abandoned_in_flight,
        )
        log_answer(record)
        return JSONResponse(
            contract.model_dump(mode="json"), headers=fake_headers(request.scope)
        )
    except ServingNotReadyError:  # shutdown race: the holder is closed
        return error_response(
            request,
            503,
            "not_ready",
            headers={"Retry-After": str(serving.concurrency.retry_after_not_ready_s)},
        )
    except Exception as error:  # noqa: BLE001 - fail closed, id and class only
        logger.error(
            "answer failed: request_id=%s error=%s",
            request_id_of(request),
            type(error).__name__,
        )
        return error_response(request, 500, "internal_error")
    finally:
        slot.release()
