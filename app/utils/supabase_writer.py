from __future__ import annotations

import os
from functools import lru_cache
from typing import Any


def is_supabase_configured() -> bool:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    return bool(url and key)


@lru_cache(maxsize=1)
def _client():
    try:
        from supabase import create_client  # type: ignore[import-not-found]
    except Exception as e:
        raise RuntimeError("dependency_missing: supabase") from e

    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        raise RuntimeError("supabase_not_configured: set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")

    return create_client(url, key)


def insert_public_file_texts(texts: list[str], name: str) -> int:
    if not is_supabase_configured():
        raise RuntimeError("supabase_not_configured: set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")

    resp = _client().table("file").insert({"texts": texts, "name": name}).execute()
    data = getattr(resp, "data", None)
    if not isinstance(data, list) or not data:
        raise RuntimeError("supabase_insert_failed: empty_response")

    row = data[0]
    inserted_id = row.get("id")
    if not isinstance(inserted_id, int):
        raise RuntimeError("supabase_insert_failed: missing_id")
    return inserted_id


def list_public_files(page: int, size: int) -> tuple[list[dict[str, Any]], int]:
    if not is_supabase_configured():
        raise RuntimeError("supabase_not_configured: set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")

    offset = page * size
    end = offset + size - 1
    resp = (
        _client()
        .table("file")
        .select("*", count="exact")
        .order("id", desc=False)
        .range(offset, end)
        .execute()
    )
    rows = list(resp.data or [])
    total = getattr(resp, "count", None)
    if not isinstance(total, int):
        total = len(rows)
    return rows, total


def get_public_file_by_id(file_id: int) -> dict[str, Any] | None:
    if not is_supabase_configured():
        raise RuntimeError("supabase_not_configured: set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")

    resp = _client().table("file").select("*").eq("id", file_id).limit(1).execute()
    data = resp.data
    if not isinstance(data, list) or not data:
        return None
    row = data[0]
    return row if isinstance(row, dict) else None


def delete_public_file_by_id(file_id: int) -> bool:
    if not is_supabase_configured():
        raise RuntimeError("supabase_not_configured: set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")

    resp = _client().table("file").delete().eq("id", file_id).execute()
    data = resp.data
    return isinstance(data, list) and len(data) > 0

