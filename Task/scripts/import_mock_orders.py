from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import RetailCrmConfig
from backend.retailcrm import create_order


def build_order_payload(order: dict, index: int) -> dict:
    items = [
        {
            "productName": item.get("productName"),
            "quantity": int(item.get("quantity", 1)),
            "initialPrice": float(item.get("initialPrice", 0)),
        }
        for item in order.get("items", [])
    ]

    return {
        "externalId": f"mock-order-{index + 1:03d}",
        "firstName": order.get("firstName"),
        "lastName": order.get("lastName"),
        "phone": order.get("phone"),
        "email": order.get("email"),
        "orderType": order.get("orderType"),
        "orderMethod": order.get("orderMethod"),
        "status": order.get("status"),
        "items": items,
        "delivery": order.get("delivery"),
        "customFields": order.get("customFields"),
        "customerComment": "Imported from mock_orders.json",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Import mock orders into RetailCRM")
    parser.add_argument("--retailcrm-base-url", required=True)
    parser.add_argument("--retailcrm-api-key", required=True)
    parser.add_argument("--site-code", required=True)
    parser.add_argument(
        "--orders-path",
        default=str(Path(__file__).resolve().parents[1] / "data" / "mock_orders.json"),
    )
    args = parser.parse_args()

    config = RetailCrmConfig(
        base_url=args.retailcrm_base_url.rstrip("/"),
        api_key=args.retailcrm_api_key,
        site_code=args.site_code,
    )

    orders = json.loads(Path(args.orders_path).read_text(encoding="utf-8"))
    print(f"Importing {len(orders)} mock orders into RetailCRM...")

    imported = 0
    for index, order in enumerate(orders):
        create_order(config, build_order_payload(order, index))
        imported += 1

    print(f"Done. Imported {imported} orders.")


if __name__ == "__main__":
    main()
