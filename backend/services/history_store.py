"""
Supabase-backed storage for extraction history (Postgres + Storage).
If SUPABASE_URL or SUPABASE_SERVICE_KEY are not set, all operations no-op / return empty.
"""
import os
import uuid
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

_SUPABASE_URL = os.getenv("SUPABASE_URL")
_SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
_BUCKET = "extraction-outputs"
_TABLE = "extraction_history"

_client = None


def _get_client():
    global _client
    if _client is None and _SUPABASE_URL and _SUPABASE_SERVICE_KEY:
        from supabase import create_client as create_supabase_client
        _client = create_supabase_client(_SUPABASE_URL, _SUPABASE_SERVICE_KEY)
    return _client


def is_configured() -> bool:
    return bool(_SUPABASE_URL and _SUPABASE_SERVICE_KEY)


def save_extraction(
    extraction_id: str,
    input_file_names: list[str],
    excel_bytes: bytes,
) -> None:
    """Upload Excel to Storage and insert a row into extraction_history."""
    client = _get_client()
    if not client:
        return

    path = f"{extraction_id}.xlsx"
    client.storage.from_(_BUCKET).upload(
        path,
        excel_bytes,
        file_options={"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    )
    client.table(_TABLE).insert({
        "id": extraction_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "input_file_names": input_file_names,
        "output_storage_path": path,
    }).execute()


def list_history(limit: int = 50) -> list[dict]:
    """Return list of extraction records, newest first."""
    client = _get_client()
    if not client:
        return []

    r = (
        client.table(_TABLE)
        .select("id, created_at, input_file_names, output_storage_path")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return [dict(row) for row in (r.data or [])]


def get_download_url(extraction_id: str, expiry_seconds: int = 3600) -> Optional[str]:
    """Return a signed URL to download the Excel file, or None if not found."""
    client = _get_client()
    if not client:
        return None

    path = f"{extraction_id}.xlsx"
    try:
        signed = client.storage.from_(_BUCKET).create_signed_url(path, expiry_seconds)
        return signed.get("signedUrl") or signed.get("path")
    except Exception:
        return None
