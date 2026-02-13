from __future__ import annotations

from functools import lru_cache
from typing import Any

from heya.shared.config.loader import load_config
from heya.shared.config.models import (
    AppConfig,
    BrowserConfig,
    CompressionConfig,
    MarkdownConfig,
    PrintConfig,
)

__all__ = [
    "AppConfig",
    "BrowserConfig",
    "PrintConfig",
    "CompressionConfig",
    "MarkdownConfig",
    "load_config",
    "get_config",
    "reset_config",
    "reload_config",
    "override_config",
]

_config_override: dict[str, Any] | None = None


@lru_cache(maxsize=1)
def _get_cached_config() -> AppConfig:
    if _config_override is not None:
        return AppConfig.from_dict(_config_override)
    return load_config()


def get_config() -> AppConfig:
    return _get_cached_config()


def reset_config() -> None:
    global _config_override
    _config_override = None
    _get_cached_config.cache_clear()


def reload_config() -> AppConfig:
    _get_cached_config.cache_clear()
    return _get_cached_config()


def override_config(config_dict: dict[str, Any]) -> None:
    global _config_override
    _config_override = config_dict if config_dict else None
    _get_cached_config.cache_clear()
