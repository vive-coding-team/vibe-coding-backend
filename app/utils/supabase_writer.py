from __future__ import annotations

import os
from functools import lru_cache


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

