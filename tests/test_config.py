from __future__ import annotations

import pytest

from heya.shared.config import (
    AppConfig,
    BrowserConfig,
    CompressionConfig,
    MarkdownConfig,
    PrintConfig,
    get_config,
    reset_config,
)


class TestBrowserConfig:
    def test_default_timeout(self):
        config = BrowserConfig()
        assert config.timeout == 3.0

    def test_default_launch_args(self):
        config = BrowserConfig()
        assert "--no-sandbox" in config.launch_args

    def test_invalid_timeout(self):
        with pytest.raises(ValueError, match="must be positive"):
            BrowserConfig(timeout=0)

        with pytest.raises(ValueError, match="must be positive"):
            BrowserConfig(timeout=-1)


class TestPrintConfig:
    def test_defaults(self):
        config = PrintConfig()
        assert config.landscape is False
        assert config.print_background is True

    def test_to_dict(self):
        config = PrintConfig()
        d = config.to_dict()
        assert "landscape" in d
        assert "print_background" in d


class TestCompressionConfig:
    def test_defaults(self):
        config = CompressionConfig()
        assert config.quality == 0
        assert config.compression_level == 9

    def test_invalid_quality(self):
        with pytest.raises(ValueError, match="quality must be 0-2"):
            CompressionConfig(quality=-1)

        with pytest.raises(ValueError, match="quality must be 0-2"):
            CompressionConfig(quality=3)

    def test_invalid_compression_level(self):
        with pytest.raises(ValueError, match="level must be 0-9"):
            CompressionConfig(compression_level=-1)

        with pytest.raises(ValueError, match="level must be 0-9"):
            CompressionConfig(compression_level=10)


class TestMarkdownConfig:
    def test_default_extensions(self):
        config = MarkdownConfig()
        assert "extra" in config.extensions
        assert "tables" in config.extensions

    def test_invalid_extensions_type(self):
        with pytest.raises(TypeError, match="must be a list"):
            MarkdownConfig(extensions="not-a-list")


class TestAppConfig:
    def test_nested_configs(self):
        config = AppConfig()
        assert isinstance(config.browser, BrowserConfig)
        assert isinstance(config.print, PrintConfig)
        assert isinstance(config.compression, CompressionConfig)
        assert isinstance(config.markdown, MarkdownConfig)

    def test_from_dict_empty(self):
        config = AppConfig.from_dict({})
        assert isinstance(config.browser, BrowserConfig)

    def test_from_dict_partial(self):
        config = AppConfig.from_dict({"browser": {"timeout": 5.0}})
        assert config.browser.timeout == 5.0


def test_get_config():
    config = get_config()
    assert isinstance(config, AppConfig)


def test_reset_config():
    config1 = get_config()
    reset_config()
    config2 = get_config()
    assert config1 is not config2
