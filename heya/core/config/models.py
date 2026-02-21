from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "BrowserConfig",
    "PrintConfig",
    "CompressionConfig",
    "MarkdownConfig",
    "AppConfig",
]


class _BrowserConstants:
    DEFAULT_TIMEOUT: float = 3.0
    DEFAULT_LAUNCH_ARGS: list[str] = ["--no-sandbox", "--disable-dev-shm-usage"]


@dataclass
class BrowserConfig:
    timeout: float = _BrowserConstants.DEFAULT_TIMEOUT
    launch_args: list[str] = field(
        default_factory=lambda: _BrowserConstants.DEFAULT_LAUNCH_ARGS
    )

    def __post_init__(self) -> None:
        if self.timeout <= 0:
            raise ValueError(f"Browser timeout must be positive, got {self.timeout}")


@dataclass
class PrintConfig:
    landscape: bool = False
    display_header_footer: bool = False
    print_background: bool = True
    prefer_css_page_size: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "landscape": self.landscape,
            "display_header_footer": self.display_header_footer,
            "print_background": self.print_background,
            "prefer_css_page_size": self.prefer_css_page_size,
        }


@dataclass
class CompressionConfig:
    quality: int = 0
    compression_level: int = 9

    def __post_init__(self) -> None:
        if not 0 <= self.quality <= 2:
            raise ValueError(f"Compression quality must be 0-2, got {self.quality}")
        if not 0 <= self.compression_level <= 9:
            raise ValueError(
                f"Compression level must be 0-9, got {self.compression_level}"
            )


@dataclass
class MarkdownConfig:
    extensions: list[str] = field(
        default_factory=lambda: [
            "extra",
            "codehilite",
            "tables",
            "fenced_code",
            "nl2br",
            "sane_lists",
        ]
    )
    extension_configs: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "codehilite": {"guess_lang": False},
        }
    )

    def __post_init__(self) -> None:
        if not isinstance(self.extensions, list):
            raise TypeError("Markdown extensions must be a list")


@dataclass
class AppConfig:
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    print: PrintConfig = field(default_factory=PrintConfig)
    compression: CompressionConfig = field(default_factory=CompressionConfig)
    markdown: MarkdownConfig = field(default_factory=MarkdownConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        return cls(
            browser=BrowserConfig(**data.get("browser", {})),
            print=PrintConfig(**data.get("print", {})),
            compression=CompressionConfig(**data.get("compression", {})),
            markdown=MarkdownConfig(**data.get("markdown", {})),
        )
