from __future__ import annotations

import pytest

from heya.core.models import (
    COMPRESSION_QUALITY_MAX,
    COMPRESSION_QUALITY_MIN,
    ConvertResult,
    is_valid_compression_quality,
)


class TestCompressionQuality:
    def test_quality_range(self):
        assert COMPRESSION_QUALITY_MIN == 0
        assert COMPRESSION_QUALITY_MAX == 2

    @pytest.mark.parametrize("value,expected", [(0, True), (1, True), (2, True), (3, False), (-1, False)])
    def test_is_valid(self, value, expected):
        assert is_valid_compression_quality(value) == expected


class TestConvertResult:
    def test_success_result(self):
        result = ConvertResult(success=True, output_path="/path/to/file.pdf", duration=1.5)
        assert result.success is True
        assert result.output_path == "/path/to/file.pdf"
        assert result.duration == 1.5
        assert result.error_message is None

    def test_failure_result(self):
        result = ConvertResult(success=False, error_message="Something went wrong")
        assert result.success is False
        assert result.output_path is None
        assert result.error_message == "Something went wrong"
