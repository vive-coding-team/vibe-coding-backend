from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.utils.extractors import ExtractResult, extract_text_from_upload

bp = Blueprint("extract", __name__)


@bp.post("/extract")
def extract():
    uploads = []

    if "files" in request.files:
        uploads.extend(request.files.getlist("files"))
    if "file" in request.files:
        uploads.append(request.files["file"])

    results: list[ExtractResult] = []

    for upload in uploads:
        if not upload or not upload.filename:
            continue
        results.append(extract_text_from_upload(upload))

    payload = {
        "count": len(results),
        "results": [
            {
                "filename": r.filename,
                "content_type": r.content_type,
                "ok": r.ok,
                "body": getattr(r, "body", []) or [],
                "error": r.error,
            }
            for r in results
        ],
    }
    return jsonify(payload), 200

