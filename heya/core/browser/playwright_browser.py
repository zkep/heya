from __future__ import annotations

from contextlib import asynccontextmanager
from types import TracebackType
from typing import Any

from playwright.async_api import async_playwright

from heya.core.models import PdfContent
from heya.core.browser.constants import BrowserConstants
from heya.core.browser.scroll_constants import ScrollConstants
from heya.core.config import PrintConfig, load_config
from heya.core.logging import get_logger

__all__ = ["PlaywrightBrowser", "BrowserSession"]

logger = get_logger(__name__)


class BrowserSession:
    def __init__(
        self,
        timeout: float,
        launch_args: list[str],
        print_config: PrintConfig,
    ) -> None:
        self.timeout = timeout
        self.launch_args = launch_args
        self._print_config = print_config
        self._browser: Any = None
        self._playwright: Any = None

    async def __aenter__(self) -> "BrowserSession":
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(args=self.launch_args)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def render(self, url: str, print_options: dict[str, Any] | None = None) -> bytes:
        assert self._browser is not None
        page = await self._browser.new_page()
        try:
            return await self._render_page(page, url, print_options)
        finally:
            await page.close()

    async def _render_page(
        self,
        page: Any,
        url: str,
        print_options: dict[str, Any] | None,
    ) -> bytes:
        if url.startswith("file://"):
            with open(url.replace("file://", ""), "r", encoding="utf-8") as f:
                html_content = f.read()
            await page.set_content(html_content)
        else:
            await page.goto(
                url, timeout=int(self.timeout * BrowserConstants.TIMEOUT_MULTIPLIER)
            )
        await self._scroll_to_bottom(page)
        calculated_print_options = self._print_config.to_dict()
        if print_options:
            calculated_print_options.update(print_options)
        pdf = await page.pdf(**calculated_print_options)
        return bytes(pdf)

    async def _scroll_to_bottom(self, page: Any) -> None:
        await page.evaluate(
            """
            ([distance, interval]) => {
                return new Promise((resolve) => {
                    let totalHeight = 0;
                    const timer = setInterval(() => {
                        const scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        if (totalHeight >= scrollHeight) {
                            clearInterval(timer);
                            resolve();
                        }
                    }, interval);
                });
            }
            """,
            [ScrollConstants.SCROLL_DISTANCE, ScrollConstants.SCROLL_INTERVAL],
        )


@asynccontextmanager
async def _create_temp_session(
    timeout: float,
    launch_args: list[str],
    print_config: PrintConfig,
):
    session = BrowserSession(timeout, launch_args, print_config)
    try:
        await session.__aenter__()
        yield session
    finally:
        await session.close()


class PlaywrightBrowser:
    def __init__(
        self,
        timeout: float | None = None,
        launch_args: list[str] | None = None,
        print_config: PrintConfig | None = None,
    ) -> None:
        config = load_config()
        self._timeout = timeout if timeout is not None else config.browser.timeout
        self._launch_args = (
            launch_args if launch_args is not None else config.browser.launch_args
        )
        self._print_config = print_config or config.print
        self._session: BrowserSession | None = None

    async def __aenter__(self) -> "PlaywrightBrowser":
        self._session = BrowserSession(
            self._timeout, self._launch_args, self._print_config
        )
        await self._session.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._session:
            await self._session.__aexit__(exc_type, exc_val, exc_tb)
            self._session = None

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    async def render_to_pdf(
        self,
        url: str,
        print_options: dict[str, Any] | None = None,
    ) -> PdfContent:
        if self._session is not None:
            data = await self._session.render(url, print_options)
        else:
            async with _create_temp_session(
                self._timeout, self._launch_args, self._print_config
            ) as session:
                data = await session.render(url, print_options)

        return PdfContent(data)
