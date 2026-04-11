from __future__ import annotations

import time
import uuid

import structlog
from flask import Flask, g, request
from structlog.contextvars import bind_contextvars, clear_contextvars


def register_request_logging(app: Flask) -> None:
    log = structlog.get_logger("http")

    @app.before_request
    def _bind_request_context() -> None:
        rid = str(uuid.uuid4())
        g.request_id = rid
        g._request_start_perf = time.perf_counter()
        bind_contextvars(request_id=rid)
        q = request.query_string.decode(errors="replace") if request.query_string else ""
        if len(q) > 500:
            q = q[:500] + "…"
        log.info(
            "request_started",
            method=request.method,
            path=request.path,
            query=q or None,
            endpoint=request.endpoint,
            remote_addr=request.remote_addr,
            content_length=request.content_length,
        )

    @app.after_request
    def _log_response(response):
        start = getattr(g, "_request_start_perf", None)
        duration_ms = (time.perf_counter() - start) * 1000 if start is not None else None
        log.info(
            "request_finished",
            status_code=response.status_code,
            duration_ms=round(duration_ms, 3) if duration_ms is not None else None,
            response_content_length=response.content_length,
        )
        return response

    @app.teardown_request
    def _clear_context(_exc: BaseException | None) -> None:
        clear_contextvars()
