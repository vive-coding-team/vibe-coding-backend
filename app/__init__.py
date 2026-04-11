from __future__ import annotations

import os

from flask import Flask

from app.logging_config import configure_logging
from app.request_logging import register_request_logging


def create_app() -> Flask:
    try:
        from dotenv import load_dotenv  # type: ignore[import-not-found]

        load_dotenv()
    except Exception:
        pass

    configure_logging()
    app = Flask(__name__)
    register_request_logging(app)
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", str(50 * 1024 * 1024)))

    from app.routes.extract import bp as extract_bp
    from app.routes.files import bp as files_bp

    app.register_blueprint(extract_bp)
    app.register_blueprint(files_bp)
    return app

