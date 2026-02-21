from __future__ import annotations

import os
from typing import Any

from heya.core.config.models import AppConfig
from heya.core.logging import get_logger

logger = get_logger(__name__)


def _load_config_from_env() -> dict[str, Any]:
    config: dict[str, Any] = {}

    if (timeout := os.getenv("HEYA_BROWSER_TIMEOUT")) is not None:
        config.setdefault("browser", {})["timeout"] = float(timeout)

    if (launch_args := os.getenv("HEYA_BROWSER_LAUNCH_ARGS")) is not None:
        config.setdefault("browser", {})["launch_args"] = launch_args.split(",")

    if (landscape := os.getenv("HEYA_PRINT_LANDSCAPE")) is not None:
        config.setdefault("print", {})["landscape"] = landscape.lower() in (
            "true",
            "1",
            "yes",
        )

    if (print_bg := os.getenv("HEYA_PRINT_BACKGROUND")) is not None:
        config.setdefault("print", {})["print_background"] = print_bg.lower() in (
            "true",
            "1",
            "yes",
        )

    if (quality := os.getenv("HEYA_COMPRESSION_QUALITY")) is not None:
        config.setdefault("compression", {})["quality"] = int(quality)

    if (extensions := os.getenv("HEYA_MARKDOWN_EXTENSIONS")) is not None:
        config.setdefault("markdown", {})["extensions"] = extensions.split(",")

    return config


def _load_config_from_file() -> dict[str, Any]:
    config_files = [
        "heya.toml",
        "heya.yaml",
        "heya.yml",
        "heya.json",
        ".heya.toml",
        ".heya.yaml",
        ".heya.yml",
        ".heya.json",
    ]

    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                if config_file.endswith(".toml"):
                    import tomllib

                    with open(config_file, "rb") as f:
                        return tomllib.load(f).get("tool", {}).get(
                            "heya", {}
                        ) or tomllib.load(f)
                elif config_file.endswith((".yaml", ".yml")):
                    try:
                        import yaml
                    except ImportError:
                        continue
                    try:
                        with open(config_file, encoding="utf-8") as f:
                            return yaml.safe_load(f) or {}
                    except Exception:
                        pass
                elif config_file.endswith(".json"):
                    import json

                    with open(config_file, encoding="utf-8") as f:
                        return json.load(f) or {}
            except Exception:
                pass

    if os.path.exists("pyproject.toml"):
        try:
            import tomllib

            with open("pyproject.toml", "rb") as f:
                result: dict[str, Any] = tomllib.load(f).get("tool", {}).get("heya", {})
                return result
        except Exception:
            pass

    return {}


def load_config() -> AppConfig:
    file_config = _load_config_from_file()
    env_config = _load_config_from_env()

    merged: dict[str, Any] = {}
    for key in ("browser", "print", "compression", "markdown"):
        merged[key] = {**file_config.get(key, {}), **env_config.get(key, {})}

    return AppConfig.from_dict(merged)
