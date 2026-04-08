from __future__ import annotations

import os

from flask import Flask


def create_app() -> Flask:
    try:
        from dotenv import load_dotenv  # type: ignore[import-not-found]

        load_dotenv()
    except Exception:
        pass

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", str(50 * 1024 * 1024)))

    from app.routes.extract import bp as extract_bp

    app.register_blueprint(extract_bp)
    return app

