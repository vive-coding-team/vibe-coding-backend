from __future__ import annotations

import structlog
from flask import Blueprint, jsonify, request

from app.utils.extractors import ExtractResult, extract_text_from_upload
from app.utils.supabase_writer import insert_public_file_texts

bp = Blueprint("extract", __name__)
_log = structlog.get_logger("extract")


def _extraction_http_error(r: ExtractResult):
    err = r.error or "extraction_failed"
    if err == "unsupported_extension":
        return jsonify({"error": "unsupported_extension"}), 400
    if err == "empty_file":
        return jsonify({"error": "empty_file"}), 400
    if "dependency_missing" in err:
        return jsonify({"error": err}), 503
    return jsonify({"error": err, "filename": r.filename}), 422


@bp.post("/extraction")
def extraction():
    upload = request.files.get("file")
    if not upload or not upload.filename:
        _log.warning("extraction_rejected", reason="missing_file")
        return jsonify({"error": "missing_file"}), 400

    r = extract_text_from_upload(upload)
    if not r.ok:
        _log.info(
            "extraction_failed",
            filename=r.filename,
            content_type=r.content_type,
            error=r.error,
        )
        return _extraction_http_error(r)

    sb: dict[str, object] = {"ok": False, "id": None, "error": None}
    if r.ok:
        try:
            sb["id"] = insert_public_file_texts(r.body, r.filename)
            sb["ok"] = True
        except Exception as e:  # noqa: BLE001 - boundary catches for API response
            sb["error"] = f"{type(e).__name__}: {e}"
            _log.error("supabase_insert_failed", filename=r.filename, exc_info=True)

    _log.info(
        "extraction_completed",
        filename=r.filename,
        content_type=r.content_type,
        text_parts=len(r.body) if r.body else 0,
        supabase_ok=bool(sb.get("ok")),
        supabase_id=sb.get("id"),
        supabase_error=sb.get("error"),
    )

    payload = {
        "count": 1,
        "results": [
            {
                "filename": r.filename,
                "content_type": r.content_type,
                "ok": r.ok,
                "body": getattr(r, "body", []) or [],
                "error": r.error,
                "supabase": sb,
            }
        ],
    }
    return jsonify(payload), 200

