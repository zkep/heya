from __future__ import annotations

import pytest

from heya.domain import (
    CompressError,
    ConfigError,
    ConvertError,
    ErrorCode,
    HeyaError,
    MarkdownError,
)


class TestHeyaExceptions:
    def test_heya_error(self):
        with pytest.raises(HeyaError) as exc_info:
            raise HeyaError("Test error")
        assert str(exc_info.value) == "Test error"

    def test_heya_error_with_code(self):
        error = HeyaError("Test", ErrorCode.INVALID_CONFIG)
        assert error.code == ErrorCode.INVALID_CONFIG

    def test_heya_error_default_code(self):
        error = HeyaError("Test")
        assert error.code == ErrorCode.UNKNOWN

    def test_convert_error_is_heya_error(self):
        error = ConvertError("Conversion failed")
        assert isinstance(error, HeyaError)

    def test_convert_error_code(self):
        error = ConvertError("Conversion failed")
        assert error.code == ErrorCode.CONVERT_FAILED

    def test_compress_error_is_heya_error(self):
        error = CompressError("Compression failed")
        assert isinstance(error, HeyaError)

    def test_compress_error_code(self):
        error = CompressError("Compression failed")
        assert error.code == ErrorCode.COMPRESS_FAILED

    def test_markdown_error_is_heya_error(self):
        error = MarkdownError("Markdown conversion failed")
        assert isinstance(error, HeyaError)

    def test_config_error(self):
        error = ConfigError("Invalid config")
        assert isinstance(error, HeyaError)
        assert error.code == ErrorCode.INVALID_CONFIG

    def test_error_chaining(self):
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise ConvertError("Wrapped error") from e
        except ConvertError as e:
            assert isinstance(e.__cause__, ValueError)


class TestErrorCode:
    def test_error_code_values(self):
        assert ErrorCode.UNKNOWN == 1000
        assert ErrorCode.CONVERT_FAILED == 1001
        assert ErrorCode.COMPRESS_FAILED == 1002
        assert ErrorCode.MARKDOWN_PARSE_FAILED == 1003

    def test_error_code_ranges(self):
        general_errors = [ErrorCode.UNKNOWN, ErrorCode.CONVERT_FAILED, ErrorCode.COMPRESS_FAILED, ErrorCode.MARKDOWN_PARSE_FAILED]
        config_errors = [ErrorCode.INVALID_CONFIG, ErrorCode.INVALID_QUALITY]
        file_errors = [ErrorCode.FILE_NOT_FOUND]
        browser_errors = [ErrorCode.BROWSER_ERROR]

        for e in general_errors:
            assert 1000 <= e < 2000
        for e in config_errors:
            assert 2000 <= e < 3000
        for e in file_errors:
            assert 3000 <= e < 4000
        for e in browser_errors:
            assert 4000 <= e < 5000
