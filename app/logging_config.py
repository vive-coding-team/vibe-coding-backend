from __future__ import annotations

import logging
import os
import sys

import structlog


def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    fmt = os.getenv("LOG_FORMAT", "console").lower()
    log_level = getattr(logging, level_name, logging.INFO)

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    shared = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if fmt == "json":
        processors = shared + [structlog.processors.JSONRenderer()]
    else:
        processors = shared + [structlog.dev.ConsoleRenderer(colors=sys.stdout.isatty())]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Align stdlib loggers with the same level; reduce duplicate HTTP noise from Werkzeug.
    logging.basicConfig(level=log_level, format="%(message)s", stream=sys.stdout, force=True)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
