from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.utils.extractors import ExtractResult, extract_text_from_upload
from app.utils.supabase_writer import insert_public_file_texts

bp = Blueprint("extract", __name__)


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
        return jsonify({"error": "missing_file"}), 400

    r = extract_text_from_upload(upload)
    if not r.ok:
        return _extraction_http_error(r)

    sb: dict[str, object] = {"ok": False, "id": None, "error": None}
    if r.ok:
        try:
            sb["id"] = insert_public_file_texts(r.body, r.filename)
            sb["ok"] = True
        except Exception as e:  # noqa: BLE001 - boundary catches for API response
            sb["error"] = f"{type(e).__name__}: {e}"

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

