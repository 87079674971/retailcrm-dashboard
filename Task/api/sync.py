from backend.config import get_sync_secret
from backend.workflow import sync_all_orders, notify_for_high_value_orders
from backend.server import JsonRequest, make_json_app


def handler(request: JsonRequest):
    secret = request.query_value("secret")

    if secret != get_sync_secret():
        return 401, {"ok": False, "error": "Invalid sync secret"}

    result = sync_all_orders()
    notifications = notify_for_high_value_orders(result["rows"])

    return 200, {
        "ok": True,
        "syncedOrders": result["count"],
        "sentNotifications": len(notifications),
    }


app = make_json_app(handler, allowed_methods=("GET", "POST"))
