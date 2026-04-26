from __future__ import annotations

from urllib.parse import urlencode

from backend.config import SupabaseConfig
from backend.net import request_json


def _build_url(config: SupabaseConfig, table: str, query: dict[str, object] | None = None) -> str:
    base = f"{config.url}/rest/v1/{table}"
    if not query:
        return base
    return f"{base}?{urlencode({key: value for key, value in query.items() if value not in (None, '')})}"


def _request_supabase(
    config: SupabaseConfig,
    table: str,
    *,
    method: str = "GET",
    query: dict[str, object] | None = None,
    json_body=None,
    prefer: str | None = None,
):
    headers = {
        "apikey": config.service_role_key,
        "Authorization": f"Bearer {config.service_role_key}",
        "Accept": "application/json",
    }

    if prefer:
        headers["Prefer"] = prefer

    return request_json(
        _build_url(config, table, query),
        method=method,
        headers=headers,
        json_body=json_body,
    )


def upsert_orders(config: SupabaseConfig, rows: list[dict]) -> list[dict]:
    if not rows:
        return []

    data = _request_supabase(
        config,
        "orders",
        method="POST",
        query={"on_conflict": "retailcrm_id"},
        prefer="resolution=merge-duplicates,return=representation",
        json_body=rows,
    )
    return data or []


def fetch_orders(config: SupabaseConfig, limit: int = 1000) -> list[dict]:
    data = _request_supabase(
        config,
        "orders",
        query={
            "select": "retailcrm_id,order_number,status,first_name,last_name,city,order_total,item_count,retailcrm_created_at,phone",
            "order": "retailcrm_created_at.desc",
            "limit": limit,
        },
    )
    return data or []


def fetch_notified_order_ids(config: SupabaseConfig, order_ids: list[int]) -> set[int]:
    if not order_ids:
        return set()

    data = _request_supabase(
        config,
        "telegram_notifications",
        query={
            "select": "retailcrm_id",
            "retailcrm_id": f"in.({','.join(str(order_id) for order_id in order_ids)})",
        },
    )
    return {int(row["retailcrm_id"]) for row in (data or []) if row.get("retailcrm_id") is not None}


def insert_notifications(config: SupabaseConfig, rows: list[dict]) -> list[dict]:
    if not rows:
        return []

    data = _request_supabase(
        config,
        "telegram_notifications",
        method="POST",
        query={"on_conflict": "retailcrm_id"},
        prefer="resolution=merge-duplicates,return=representation",
        json_body=rows,
    )
    return data or []
