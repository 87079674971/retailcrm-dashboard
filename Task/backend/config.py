from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RetailCrmConfig:
    base_url: str
    api_key: str
    site_code: str


@dataclass(frozen=True)
class SupabaseConfig:
    url: str
    service_role_key: str


@dataclass(frozen=True)
class TelegramConfig:
    bot_token: str
    chat_id: str


def _trim_trailing_slash(value: str) -> str:
    return value.rstrip("/")


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_retailcrm_config_from_env() -> RetailCrmConfig:
    return RetailCrmConfig(
        base_url=_trim_trailing_slash(_require_env("RETAILCRM_BASE_URL")),
        api_key=_require_env("RETAILCRM_API_KEY"),
        site_code=_require_env("RETAILCRM_SITE_CODE"),
    )


def get_supabase_config_from_env() -> SupabaseConfig:
    return SupabaseConfig(
        url=_trim_trailing_slash(_require_env("SUPABASE_URL")),
        service_role_key=_require_env("SUPABASE_SERVICE_ROLE_KEY"),
    )


def get_telegram_config_from_env() -> TelegramConfig:
    return TelegramConfig(
        bot_token=_require_env("TELEGRAM_BOT_TOKEN"),
        chat_id=_require_env("TELEGRAM_CHAT_ID"),
    )


def get_notification_threshold() -> float:
    raw = os.getenv("NOTIFICATION_THRESHOLD", "50000")
    try:
        return float(raw)
    except ValueError as exc:
        raise RuntimeError("NOTIFICATION_THRESHOLD must be numeric") from exc


def get_webhook_secret() -> str:
    return _require_env("WEBHOOK_SECRET")


def get_sync_secret() -> str:
    return _require_env("SYNC_SECRET")
