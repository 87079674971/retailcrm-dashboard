from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import get_supabase_config_from_env
from backend.dashboard import build_dashboard_payload
from backend.server import JsonRequest, make_json_app
from backend.supabase import fetch_orders


def handle_request(_: JsonRequest) -> tuple[int, dict]:
    orders = fetch_orders(get_supabase_config_from_env(), limit=1000)
    payload = build_dashboard_payload(orders, days=14)
    return 200, {"ok": True, **payload}


app = make_json_app(handle_request, allowed_methods=("GET",))
