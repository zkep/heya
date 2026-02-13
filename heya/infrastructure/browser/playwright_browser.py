from __future__ import annotations

from contextlib import contextmanager
from types import TracebackType
from typing import Any, Iterator

from playwright.sync_api import sync_playwright

from heya.domain import PdfContent
from heya.shared import BrowserConstants, ScrollConstants
from heya.shared.config import PrintConfig, get_config
from heya.shared.logging import get_logger

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

    def __enter__(self) -> "BrowserSession":
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(args=self.launch_args)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None

    def render(self, url: str, print_options: dict[str, Any] | None = None) -> bytes:
        assert self._browser is not None
        page = self._browser.new_page()
        try:
            return self._render_page(page, url, print_options)
        finally:
            page.close()

    def _render_page(
        self,
        page: Any,
        url: str,
        print_options: dict[str, Any] | None,
    ) -> bytes:
        if url.startswith("file://"):
            with open(url.replace("file://", ""), "r", encoding="utf-8") as f:
                html_content = f.read()
            page.set_content(html_content)
        else:
            page.goto(
                url, timeout=int(self.timeout * BrowserConstants.TIMEOUT_MULTIPLIER)
            )
        self._scroll_to_bottom(page)
        calculated_print_options = self._print_config.to_dict()
        if print_options:
            calculated_print_options.update(print_options)
        pdf = page.pdf(**calculated_print_options)
        return bytes(pdf)

    def _scroll_to_bottom(self, page: Any) -> None:
        page.evaluate(
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


@contextmanager
def _create_temp_session(
    timeout: float,
    launch_args: list[str],
    print_config: PrintConfig,
) -> Iterator[BrowserSession]:
    session = BrowserSession(timeout, launch_args, print_config)
    try:
        session.__enter__()
        yield session
    finally:
        session.close()


class PlaywrightBrowser:
    def __init__(
        self,
        timeout: float | None = None,
        launch_args: list[str] | None = None,
        print_config: PrintConfig | None = None,
    ) -> None:
        config = get_config()
        self._timeout = timeout if timeout is not None else config.browser.timeout
        self._launch_args = (
            launch_args if launch_args is not None else config.browser.launch_args
        )
        self._print_config = print_config or config.print
        self._session: BrowserSession | None = None

    def __enter__(self) -> "PlaywrightBrowser":
        self._session = BrowserSession(
            self._timeout, self._launch_args, self._print_config
        )
        self._session.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._session:
            self._session.__exit__(exc_type, exc_val, exc_tb)
            self._session = None

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None

    def render_to_pdf(
        self,
        url: str,
        print_options: dict[str, Any] | None = None,
    ) -> PdfContent:
        if self._session is not None:
            data = self._session.render(url, print_options)
        else:
            with _create_temp_session(
                self._timeout, self._launch_args, self._print_config
            ) as session:
                data = session.render(url, print_options)

        return PdfContent(data)
