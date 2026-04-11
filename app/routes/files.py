from __future__ import annotations

import structlog
from flask import Blueprint, jsonify, request

from app.utils.supabase_writer import (
    delete_public_file_by_id,
    get_public_file_by_id,
    is_supabase_configured,
    list_public_files,
)

bp = Blueprint("files", __name__, url_prefix="/file")
_log = structlog.get_logger("files")


def _parse_page_size() -> tuple[int, int]:
    try:
        page = int(request.args.get("page", "0"))
    except ValueError:
        page = 0
    try:
        size = int(request.args.get("size", "5"))
    except ValueError:
        size = 5
    if page < 0:
        page = 0
    if size < 1:
        size = 5
    if size > 200:
        size = 200
    return page, size


@bp.get("")
def list_files():
    if not is_supabase_configured():
        _log.warning("list_files_unavailable", reason="supabase_not_configured")
        return jsonify({"error": "supabase_not_configured"}), 503
    page, size = _parse_page_size()
    try:
        items, total = list_public_files(page, size)
    except Exception as e:  # noqa: BLE001
        _log.error("list_files_failed", page=page, size=size, exc_info=True)
        return jsonify({"error": f"{type(e).__name__}: {e}"}), 500
    _log.info("list_files_ok", page=page, size=size, total=total, returned=len(items))
    return (
        jsonify(
            {
                "page": page,
                "size": size,
                "total": total,
                "items": items,
            }
        ),
        200,
    )


@bp.get("/<int:file_id>")
def get_file(file_id: int):
    if not is_supabase_configured():
        _log.warning("get_file_unavailable", reason="supabase_not_configured", file_id=file_id)
        return jsonify({"error": "supabase_not_configured"}), 503
    try:
        row = get_public_file_by_id(file_id)
    except Exception as e:  # noqa: BLE001
        _log.error("get_file_failed", file_id=file_id, exc_info=True)
        return jsonify({"error": f"{type(e).__name__}: {e}"}), 500
    if row is None:
        _log.info("get_file_not_found", file_id=file_id)
        return jsonify({"error": "not_found"}), 404
    _log.info("get_file_ok", file_id=file_id)
    return jsonify(row), 200


@bp.delete("/<int:file_id>")
def delete_file(file_id: int):
    if not is_supabase_configured():
        _log.warning("delete_file_unavailable", reason="supabase_not_configured", file_id=file_id)
        return jsonify({"error": "supabase_not_configured"}), 503
    try:
        deleted = delete_public_file_by_id(file_id)
    except Exception as e:  # noqa: BLE001
        _log.error("delete_file_failed", file_id=file_id, exc_info=True)
        return jsonify({"error": f"{type(e).__name__}: {e}"}), 500
    if not deleted:
        _log.info("delete_file_not_found", file_id=file_id)
        return jsonify({"error": "not_found"}), 404
    _log.info("delete_file_ok", file_id=file_id)
    return jsonify({"ok": True, "id": file_id}), 200
