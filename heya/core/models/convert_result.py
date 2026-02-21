from __future__ import annotations

from dataclasses import dataclass

__all__ = ["ConvertResult"]


@dataclass
class ConvertResult:
    success: bool
    output_path: str | None = None
    error_message: str | None = None
    duration: float = 0.0
