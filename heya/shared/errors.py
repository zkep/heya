from __future__ import annotations

from heya.domain.exceptions import ErrorCode, HeyaError

__all__ = ["ErrorFormatter", "format_error"]

_ERROR_MESSAGES = {
    ErrorCode.UNKNOWN: "An unknown error occurred",
    ErrorCode.CONVERT_FAILED: "Conversion failed",
    ErrorCode.COMPRESS_FAILED: "PDF compression failed",
    ErrorCode.MARKDOWN_PARSE_FAILED: "Failed to parse Markdown",
    ErrorCode.INVALID_CONFIG: "Invalid configuration",
    ErrorCode.INVALID_QUALITY: "Invalid quality level",
    ErrorCode.FILE_NOT_FOUND: "File not found",
    ErrorCode.BROWSER_ERROR: "Browser error occurred",
}


class ErrorFormatter:
    @staticmethod
    def format_exception(e: Exception) -> str:
        if isinstance(e, HeyaError):
            base_msg = _ERROR_MESSAGES.get(e.code, _ERROR_MESSAGES[ErrorCode.UNKNOWN])
            if str(e):
                return f"{base_msg}: {e}"
            return base_msg
        return str(e)

    @staticmethod
    def get_error_message(code: ErrorCode) -> str:
        return _ERROR_MESSAGES.get(code, _ERROR_MESSAGES[ErrorCode.UNKNOWN])


def format_error(e: Exception) -> str:
    return ErrorFormatter.format_exception(e)
