from __future__ import annotations

from backend.config import (
    get_notification_threshold,
    get_retailcrm_config_from_env,
    get_supabase_config_from_env,
    get_telegram_config_from_env,
)
from backend.retailcrm import fetch_all_orders, fetch_order_by_id
from backend.supabase import (
    fetch_notified_order_ids,
    insert_notifications,
    upsert_orders,
)
from backend.telegram_client import build_large_order_message, send_telegram_message
from backend.transform import normalize_retailcrm_order


def sync_all_orders() -> dict:
    retailcrm_config = get_retailcrm_config_from_env()
    supabase_config = get_supabase_config_from_env()
    orders = fetch_all_orders(retailcrm_config)
    rows = [normalize_retailcrm_order(order) for order in orders if order.get("id") is not None]
    synced = upsert_orders(supabase_config, rows)
    return {"count": len(synced), "rows": synced}


def sync_single_order(order_id: int | str) -> dict:
    retailcrm_config = get_retailcrm_config_from_env()
    supabase_config = get_supabase_config_from_env()
    order = fetch_order_by_id(retailcrm_config, order_id)
    row = normalize_retailcrm_order(order)

    if row.get("retailcrm_id") is None:
        raise RuntimeError("RetailCRM order does not contain numeric id")

    synced = upsert_orders(supabase_config, [row])
    return synced[0] if synced else row


def notify_for_high_value_orders(rows: list[dict]) -> list[dict]:
    threshold = get_notification_threshold()
    supabase_config = get_supabase_config_from_env()
    telegram_config = get_telegram_config_from_env()

    candidates = [row for row in rows if float(row.get("order_total") or 0) > threshold]
    if not candidates:
        return []

    notified_ids = fetch_notified_order_ids(
        supabase_config,
        [int(row["retailcrm_id"]) for row in candidates if row.get("retailcrm_id") is not None],
    )

    saved_rows = []

    for row in candidates:
        retailcrm_id = int(row["retailcrm_id"])
        if retailcrm_id in notified_ids:
            continue

        message_text = build_large_order_message(row)
        telegram_result = send_telegram_message(telegram_config, message_text)
        saved_rows.append(
            {
                "retailcrm_id": retailcrm_id,
                "order_total": float(row.get("order_total") or 0),
                "message_text": message_text,
                "telegram_chat_id": str(telegram_config.chat_id),
                "telegram_message_id": telegram_result.get("message_id"),
            }
        )

    insert_notifications(supabase_config, saved_rows)
    return saved_rows
