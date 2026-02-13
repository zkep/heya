from __future__ import annotations

import os

from heya.domain import MarkdownError
from heya.infrastructure.template.html_template import render_html
from heya.shared.config import MarkdownConfig, get_config
from heya.shared.logging import get_logger

__all__ = ["MarkdownProcessor"]

logger = get_logger(__name__)


class MarkdownProcessor:
    def __init__(
        self,
        config: MarkdownConfig | None = None,
    ) -> None:
        self._config = config or get_config().markdown

    def convert_to_html(self, md_file: str) -> str:
        if not os.path.isfile(md_file):
            raise MarkdownError(f"Markdown file not found: {md_file}")

        try:
            import markdown
        except ImportError:
            raise MarkdownError(
                "markdown package is required. Install with: pip install markdown"
            )

        with open(md_file, encoding="utf-8") as f:
            md_content = f.read()

        html_content = markdown.markdown(
            md_content,
            extensions=self._config.extensions,
            extension_configs=self._config.extension_configs,
        )

        title = os.path.splitext(os.path.basename(md_file))[0]
        full_html = render_html(title=title, content=html_content)

        return full_html
