"""Pure ASGI middleware: server request ID and the answer body-size limit
(Spec 013 R9, R13). An incoming `X-Request-ID` is ignored."""

import json
import uuid
from typing import Any

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

ANSWER_PATH = "/v1/answer"
FAKE_HEADER = "X-W2A-Fake"


def fake_headers(scope: Scope) -> dict[str, str]:
    """`X-W2A-Fake: true` on every answer response in fake mode."""
    if scope.get("path") != ANSWER_PATH:
        return {}
    app = scope.get("app")
    settings = getattr(getattr(app, "state", None), "settings", None)
    if settings is not None and settings.api_fake:
        return {FAKE_HEADER: "true"}
    return {}


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = uuid.uuid4().hex
        scope.setdefault("state", {})["request_id"] = request_id

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)["X-Request-ID"] = request_id
            await send(message)

        await self.app(scope, receive, send_with_id)


class BodySizeMiddleware:
    """413 before parsing, with or without `Content-Length`."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] != "http"
            or scope["method"] != "POST"
            or scope["path"] != ANSWER_PATH
        ):
            await self.app(scope, receive, send)
            return
        limit: int = scope["app"].state.serving_config.request.max_body_bytes
        declared = dict(scope["headers"]).get(b"content-length", b"")
        if declared.isdigit() and int(declared) > limit:
            await self._too_large(scope, send)
            return
        chunks: list[bytes] = []
        total = 0
        more = True
        while more:
            message = await receive()
            if message["type"] != "http.request":
                await self.app(scope, receive, send)
                return
            body: bytes = message.get("body", b"")
            total += len(body)
            if total > limit:
                await self._too_large(scope, send)
                return
            chunks.append(body)
            more = bool(message.get("more_body", False))
        replayed = False

        async def replay() -> Message:
            nonlocal replayed
            if not replayed:
                replayed = True
                return {
                    "type": "http.request",
                    "body": b"".join(chunks),
                    "more_body": False,
                }
            return await receive()

        await self.app(scope, replay, send)

    async def _too_large(self, scope: Scope, send: Send) -> None:
        state: dict[str, Any] = scope.get("state", {})
        payload = json.dumps(
            {"request_id": state.get("request_id"), "error": "body_too_large"}
        ).encode()
        headers = {"content-type": "application/json", **fake_headers(scope)}
        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [
                    *((k.lower().encode(), v.encode()) for k, v in headers.items()),
                    (b"content-length", str(len(payload)).encode()),
                ],
            }
        )
        await send({"type": "http.response.body", "body": payload})
