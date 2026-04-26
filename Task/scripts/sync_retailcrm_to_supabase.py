from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import RetailCrmConfig, SupabaseConfig
from backend.retailcrm import fetch_all_orders
from backend.supabase import upsert_orders
from backend.transform import normalize_retailcrm_order


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync RetailCRM orders into Supabase")
    parser.add_argument("--retailcrm-base-url", required=True)
    parser.add_argument("--retailcrm-api-key", required=True)
    parser.add_argument("--site-code", required=True)
    parser.add_argument("--supabase-url", required=True)
    parser.add_argument("--supabase-service-role-key", required=True)
    args = parser.parse_args()

    retailcrm_config = RetailCrmConfig(
        base_url=args.retailcrm_base_url.rstrip("/"),
        api_key=args.retailcrm_api_key,
        site_code=args.site_code,
    )
    supabase_config = SupabaseConfig(
        url=args.supabase_url.rstrip("/"),
        service_role_key=args.supabase_service_role_key,
    )

    orders = fetch_all_orders(retailcrm_config)
    print(f"Fetched {len(orders)} orders from RetailCRM.")

    rows = [normalize_retailcrm_order(order) for order in orders if order.get("id") is not None]
    result = upsert_orders(supabase_config, rows)
    print(f"Upserted {len(result)} rows into Supabase.")


if __name__ == "__main__":
    main()
