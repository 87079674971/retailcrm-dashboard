from __future__ import annotations

from datetime import datetime


def _to_number(value, fallback=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _to_iso(value: str | None) -> str | None:
    if not value:
        return None

    normalized = str(value).replace(" ", "T")
    try:
        return datetime.fromisoformat(normalized).isoformat()
    except ValueError:
        return None


def normalize_items(items: list[dict] | None) -> list[dict]:
    normalized: list[dict] = []

    for item in items or []:
        quantity = _to_number(item.get("quantity"), 1)
        initial_price = _to_number(item.get("initialPrice"), 0)
        discount_total = _to_number(item.get("discountTotal"), 0)
        normalized.append(
            {
                "productName": item.get("productName")
                or ((item.get("offer") or {}).get("name"))
                or ((item.get("offer") or {}).get("externalId"))
                or "Unknown product",
                "quantity": quantity,
                "initialPrice": initial_price,
                "discountTotal": discount_total,
                "itemTotal": quantity * max(0, initial_price - discount_total),
            }
        )

    return normalized


def compute_order_total(order: dict) -> float:
    for field in ("totalSumm", "totalAmount", "summ", "totalPrice"):
        value = _to_number(order.get(field), fallback=float("nan"))
        if value == value:
            return value

    return sum(item["itemTotal"] for item in normalize_items(order.get("items")))


def normalize_retailcrm_order(order: dict) -> dict:
    items = normalize_items(order.get("items"))
    customer = order.get("customer") or {}
    phones = customer.get("phones") or []
    first_phone = phones[0]["number"] if phones else None
    delivery = order.get("delivery") or {}
    address = delivery.get("address") or {}

    return {
        "retailcrm_id": int(order["id"]) if order.get("id") is not None else None,
        "external_id": str(order["externalId"]) if order.get("externalId") else None,
        "order_number": str(order.get("number") or order.get("id")) if order.get("id") is not None else None,
        "status": order.get("status"),
        "first_name": order.get("firstName") or customer.get("firstName"),
        "last_name": order.get("lastName") or customer.get("lastName"),
        "phone": order.get("phone") or first_phone,
        "email": order.get("email") or customer.get("email"),
        "city": address.get("city"),
        "address_text": address.get("text"),
        "order_total": compute_order_total(order),
        "item_count": int(sum(float(item["quantity"]) for item in items)),
        "utm_source": (order.get("customFields") or {}).get("utm_source"),
        "order_type": order.get("orderType"),
        "order_method": order.get("orderMethod"),
        "currency": order.get("currency") or "KZT",
        "retailcrm_created_at": _to_iso(order.get("createdAt")),
        "retailcrm_updated_at": _to_iso(order.get("updatedAt") or order.get("createdAt")),
        "items": items,
        "raw": order,
        "synced_at": datetime.utcnow().isoformat(),
    }
