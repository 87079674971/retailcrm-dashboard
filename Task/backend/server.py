from __future__ import annotations

import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Callable
from urllib.parse import parse_qs


@dataclass(frozen=True)
class JsonRequest:
    method: str
    path: str
    query: dict[str, list[str]]

    def query_value(self, key: str) -> str | None:
        values = self.query.get(key) or []
        return values[0] if values else None


JsonPayload = dict
JsonHandlerFunc = Callable[[JsonRequest], tuple[int, JsonPayload]]


def _status_text(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "OK"


def json_response(start_response, status_code: int, payload: JsonPayload):
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    start_response(
        f"{status_code} {_status_text(status_code)}",
        [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]


def make_json_app(
    handle_request: JsonHandlerFunc,
    *,
    allowed_methods: tuple[str, ...] = ("GET",),
):
    def app(environ, start_response):
        method = str(environ.get("REQUEST_METHOD", "GET")).upper()

        if method not in allowed_methods:
            return json_response(
                start_response,
                405,
                {"ok": False, "error": f"Method {method} is not allowed"},
            )

        request = JsonRequest(
            method=method,
            path=str(environ.get("PATH_INFO", "")),
            query=parse_qs(str(environ.get("QUERY_STRING", ""))),
        )

        try:
            status_code, payload = handle_request(request)
            return json_response(start_response, status_code, payload)
        except Exception as exc:  # noqa: BLE001
            return json_response(start_response, 500, {"ok": False, "error": str(exc)})

    return app
