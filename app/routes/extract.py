from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.utils.extractors import ExtractResult, extract_text_from_upload
from app.utils.supabase_writer import insert_public_file_texts

bp = Blueprint("extract", __name__)


@bp.post("/extract")
def extract():
    uploads = []

    if "files" in request.files:
        uploads.extend(request.files.getlist("files"))
    if "file" in request.files:
        uploads.append(request.files["file"])

    results: list[ExtractResult] = []
    supabase_rows: list[dict[str, object]] = []

    for upload in uploads:
        if not upload or not upload.filename:
            continue
        r = extract_text_from_upload(upload)
        results.append(r)

        sb: dict[str, object] = {"ok": False, "id": None, "error": None}
        if r.ok:
            try:
                sb["id"] = insert_public_file_texts(r.body)
                sb["ok"] = True
            except Exception as e:  # noqa: BLE001 - boundary catches for API response
                sb["error"] = f"{type(e).__name__}: {e}"
        supabase_rows.append(sb)

    payload = {
        "count": len(results),
        "results": [
            {
                "filename": r.filename,
                "content_type": r.content_type,
                "ok": r.ok,
                "body": getattr(r, "body", []) or [],
                "error": r.error,
                "supabase": supabase_rows[i] if i < len(supabase_rows) else {"ok": False, "id": None, "error": "internal_mismatch"},
            }
            for i, r in enumerate(results)
        ],
    }
    return jsonify(payload), 200

