from __future__ import annotations

from datetime import datetime

from backend.config import TelegramConfig
from backend.net import request_json


def send_telegram_message(config: TelegramConfig, text: str) -> dict:
    data = request_json(
        f"https://api.telegram.org/bot{config.bot_token}/sendMessage",
        method="POST",
        json_body={
            "chat_id": config.chat_id,
            "text": text,
        },
    )

    if not isinstance(data, dict) or not data.get("ok"):
        raise RuntimeError((data or {}).get("description") or "Telegram sendMessage failed")

    return data.get("result") or {}


def build_large_order_message(order: dict) -> str:
    customer = " ".join(part for part in [order.get("first_name"), order.get("last_name")] if part).strip() or "Без имени"
    created_at = order.get("retailcrm_created_at")

    if created_at:
        try:
            created_label = datetime.fromisoformat(created_at).strftime("%d.%m.%Y %H:%M")
        except ValueError:
            created_label = created_at
    else:
        created_label = "дата не указана"

    return "\n".join(
        [
            "Новый заказ выше 50 000 KZT",
            f"Заказ: {order.get('order_number') or order.get('retailcrm_id')}",
            f"Сумма: {int(round(float(order.get('order_total') or 0))):,} ₸".replace(",", " "),
            f"Клиент: {customer}",
            f"Телефон: {order.get('phone') or 'не указан'}",
            f"Город: {order.get('city') or 'не указан'}",
            f"Статус: {order.get('status') or 'не указан'}",
            f"Дата: {created_label}",
        ]
    )
