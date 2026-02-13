from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Generator
from typing import Any

from heya.domain import ConvertResult

__all__ = ["BaseConverter", "BaseWechatConverter"]


class BaseConverter(ABC):
    def __init__(
        self,
        convert_fn: Callable[..., ConvertResult] | None = None,
    ) -> None:
        self._convert_fn = convert_fn

    @abstractmethod
    def convert(
        self,
        source: str,
        target: str,
        **kwargs: Any,
    ) -> ConvertResult:
        pass

    @abstractmethod
    def convert_stream(
        self,
        sources: list[str],
        progress_update_fn: Callable[[int, int, str], dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> Generator[tuple[list[str] | None, dict[str, Any], dict[str, Any]], None, None]:
        pass


class BaseWechatConverter(ABC):
    def __init__(
        self,
        convert_fn: Callable[..., Any] | None = None,
    ) -> None:
        self._convert_fn = convert_fn

    @abstractmethod
    def convert(
        self,
        source: str,
        target: str,
        **kwargs: Any,
    ) -> Any:
        pass

    @abstractmethod
    def convert_stream(
        self,
        sources: list[str],
        progress_update_fn: Callable[[int, int, str], dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> Generator[tuple[list[str] | None, dict[str, Any], dict[str, Any]], None, None]:
        pass
