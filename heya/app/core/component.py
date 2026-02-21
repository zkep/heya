from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from PySide6.QtWidgets import QWidget

__all__ = ["Component", "ComponentContext"]


@dataclass
class ComponentContext:
    lang: str = "zh"
    data: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.data is None:
            self.data = {}


@runtime_checkable
class Component(Protocol):
    @property
    def name(self) -> str: ...

    def get_i18n_keys(self) -> dict[str, dict[str, str]]: ...

    def render(self, ctx: ComponentContext, parent: QWidget | None = None) -> QWidget: ...

    def setup_handlers(self) -> None: ...
