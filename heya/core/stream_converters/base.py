from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Generator
from typing import TYPE_CHECKING, Any

from heya.core.models import ConvertResult

if TYPE_CHECKING:
    from heya.core.wechat.wechat_converter import WechatConvertResult

__all__ = ["BaseConverter", "BaseWechatConverter"]


class BaseConverter(ABC):
    def __init__(
        self,
        convert_fn: Callable[..., ConvertResult] | None = None,
    ) -> None:
        self._convert_fn = convert_fn

    @abstractmethod
    async def convert(
        self,
        source: str,
        target: str,
        **kwargs: Any,
    ) -> ConvertResult:
        pass

    @abstractmethod
    async def convert_stream(
        self,
        sources: list[str],
        progress_update_fn: Callable[[int, int, str], None] | None = None,
        **kwargs: Any,
    ) -> Generator[tuple[list[str] | None, int, int, str | None], None, None]:
        pass


class BaseWechatConverter(ABC):
    def __init__(
        self,
        convert_fn: Callable[..., WechatConvertResult] | None = None,
    ) -> None:
        self._convert_fn = convert_fn

    @abstractmethod
    async def convert(
        self,
        source: str,
        target: str,
        **kwargs: Any,
    ) -> WechatConvertResult:
        pass

    @abstractmethod
    async def convert_stream(
        self,
        sources: list[str],
        progress_update_fn: Callable[[int, int, str], None] | None = None,
        **kwargs: Any,
    ) -> Generator[tuple[list[str] | None, int, int, str | None], None, None]:
        pass
