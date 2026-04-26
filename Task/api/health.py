from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.server import JsonRequest, make_json_app


def handle_request(_: JsonRequest) -> tuple[int, dict]:
    return (
        200,
        {
            "ok": True,
            "service": "rc-orders",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


app = make_json_app(handle_request, allowed_methods=("GET",))
