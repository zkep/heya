from __future__ import annotations

from enum import IntEnum


class ErrorCode(IntEnum):
    UNKNOWN = 1000
    CONVERT_FAILED = 1001
    COMPRESS_FAILED = 1002
    MARKDOWN_PARSE_FAILED = 1003
    INVALID_CONFIG = 2001
    INVALID_QUALITY = 2002
    FILE_NOT_FOUND = 3001
    BROWSER_ERROR = 4001
    WECHAT_ERROR = 4002
    PDF_TO_WORD_ERROR = 4003
    TIMEOUT_ERROR = 4004
    NETWORK_ERROR = 4005
    VALIDATION_ERROR = 5001


class HeyaError(Exception):
    code: ErrorCode = ErrorCode.UNKNOWN

    def __init__(self, message: str, code: ErrorCode | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class ConvertError(HeyaError):
    code = ErrorCode.CONVERT_FAILED


class CompressError(HeyaError):
    code = ErrorCode.COMPRESS_FAILED


class MarkdownError(HeyaError):
    code = ErrorCode.MARKDOWN_PARSE_FAILED


class ConfigError(HeyaError):
    code = ErrorCode.INVALID_CONFIG


class WechatError(HeyaError):
    code = ErrorCode.WECHAT_ERROR


class PdfToWordError(HeyaError):
    code = ErrorCode.PDF_TO_WORD_ERROR


class TimeoutError(HeyaError):
    code = ErrorCode.TIMEOUT_ERROR


class NetworkError(HeyaError):
    code = ErrorCode.NETWORK_ERROR


class ValidationError(HeyaError):
    code = ErrorCode.VALIDATION_ERROR
