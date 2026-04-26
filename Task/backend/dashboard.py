from __future__ import annotations

from datetime import datetime, timedelta


def _format_label(date_value: datetime) -> str:
    return date_value.strftime("%d.%m")


def build_dashboard_payload(orders: list[dict], days: int = 14) -> dict:
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    buckets = []
    bucket_map = {}

    for index in range(days):
        current = today - timedelta(days=days - index - 1)
        key = current.strftime("%Y-%m-%d")
        bucket = {
            "day": key,
            "label": _format_label(current),
            "orders": 0,
            "revenue": 0,
        }
        buckets.append(bucket)
        bucket_map[key] = bucket

    total_revenue = 0.0
    high_value_orders = 0
    cities: dict[str, int] = {}

    for order in orders:
        amount = float(order.get("order_total") or 0)
        total_revenue += amount

        if amount > 50000:
            high_value_orders += 1

        city = order.get("city")
        if city:
            cities[city] = cities.get(city, 0) + 1

        created_at = str(order.get("retailcrm_created_at") or "")[:10]
        if created_at in bucket_map:
            bucket_map[created_at]["orders"] += 1
            bucket_map[created_at]["revenue"] += amount

    top_cities = [
        {"city": city, "ordersCount": count}
        for city, count in sorted(cities.items(), key=lambda item: item[1], reverse=True)[:5]
    ]

    return {
        "generatedAt": datetime.utcnow().isoformat(),
        "summary": {
            "totalOrders": len(orders),
            "totalRevenue": total_revenue,
            "averageCheck": (total_revenue / len(orders)) if orders else 0,
            "highValueOrders": high_value_orders,
        },
        "series": buckets,
        "topCities": top_cities,
        "recentOrders": orders[:10],
    }
