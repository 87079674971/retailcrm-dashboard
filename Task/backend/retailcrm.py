from __future__ import annotations

import json
from urllib.parse import urlencode

from backend.config import RetailCrmConfig
from backend.net import request_json


def _build_url(base_url: str, path: str, query: dict[str, object] | None = None) -> str:
    base = f"{base_url}{path}"
    if not query:
        return base
    return f"{base}?{urlencode({key: value for key, value in query.items() if value not in (None, '')})}"


def _request_retailcrm(
    config: RetailCrmConfig,
    path: str,
    *,
    method: str = "GET",
    query: dict[str, object] | None = None,
    json_body: dict[str, object] | None = None,
    form_body: dict[str, object] | None = None,
) -> dict:
    data = request_json(
        _build_url(config.base_url, path, query),
        method=method,
        headers={
            "Accept": "application/json",
            "X-API-KEY": config.api_key,
        },
        json_body=json_body,
        form_body=form_body,
    )

    if isinstance(data, dict) and data.get("success") is False:
        raise RuntimeError(data.get("errorMsg") or "RetailCRM request failed")

    if not isinstance(data, dict):
        raise RuntimeError("RetailCRM response is not a JSON object")

    return data


def create_order(config: RetailCrmConfig, order_payload: dict) -> dict:
    data = _request_retailcrm(
        config,
        "/api/v5/orders/create",
        method="POST",
        form_body={
            "site": config.site_code,
            "order": json.dumps(order_payload, ensure_ascii=False),
        },
    )
    return data


def fetch_order_by_id(config: RetailCrmConfig, order_id: int | str) -> dict:
    data = _request_retailcrm(
        config,
        f"/api/v5/orders/{order_id}",
        query={"by": "id"},
    )
    return data.get("order") or {}


def fetch_all_orders(config: RetailCrmConfig, *, limit: int = 100, max_pages: int = 100) -> list[dict]:
    orders: list[dict] = []

    for page in range(1, max_pages + 1):
        data = _request_retailcrm(
            config,
            "/api/v5/orders",
            query={"limit": limit, "page": page},
        )
        page_orders = data.get("orders") or []
        orders.extend(page_orders)

        pagination = data.get("pagination") or {}
        current_page = int(pagination.get("currentPage", page))
        total_pages = int(pagination.get("totalPageCount", current_page))

        if not page_orders or current_page >= total_pages:
            break

    return orders
