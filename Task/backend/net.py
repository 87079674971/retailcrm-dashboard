from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import ssl


def request_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    json_body: Any | None = None,
    form_body: dict[str, Any] | None = None,
    timeout: int = 30,
) -> Any:
    request_headers = dict(headers or {})
    data = None

    if json_body is not None and form_body is not None:
        raise ValueError("Use either json_body or form_body, not both")

    if json_body is not None:
        request_headers["Content-Type"] = "application/json; charset=utf-8"
        data = json.dumps(json_body).encode("utf-8")
    elif form_body is not None:
        request_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"
        data = urlencode(form_body).encode("utf-8")

    request = Request(url, method=method.upper(), headers=request_headers, data=data)
    context = ssl._create_unverified_context()

    try: 
        with urlopen(request, timeout=timeout, context=context) as response:
            raw = response.read().decode("utf-8")
            if not raw:
                return None
            return json.loads(raw)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc
