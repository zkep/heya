from __future__ import annotations

import os
from collections.abc import Callable
from typing import TYPE_CHECKING, Generator

from heya.core.helpers import convert, convert_md, convert_wechat
from heya.core.wechat.wechat_converter import WechatConvertResult
from heya.core.exceptions import (
    CompressError,
    NetworkError,
    PdfToWordError,
    TimeoutError,
    ValidationError,
    WechatError,
)
from heya.core.models import ConvertResult
from heya.core.wechat.parser import WechatParser
from heya.core.temp.temp import create_output_path
from heya.core.stream_converters import BatchConverter, HtmlConverter, MarkdownConverter, WechatConverter
from heya.app.i18n import get_texts

if TYPE_CHECKING:
    from typing import Any

__all__ = ["AppConvertService", "ConversionError"]


class ConversionError(Exception):
    pass


class AppConvertService:
    def __init__(
        self,
        lang: str = "zh",
        convert_fn: Callable[..., ConvertResult] | None = None,
        convert_md_fn: Callable[..., ConvertResult] | None = None,
        convert_wechat_fn: Callable[..., WechatConvertResult] | None = None,
        max_workers: int = 4,
    ) -> None:
        self._lang = lang
        self._html_converter = HtmlConverter(convert_fn or convert)
        self._markdown_converter = MarkdownConverter(convert_md_fn or convert_md)
        self._wechat_converter = WechatConverter(convert_wechat_fn or convert_wechat)
        self._batch_converter = BatchConverter(convert_fn or convert, max_workers=max_workers)

    def set_language(self, lang: str) -> None:
        self._lang = lang

    def _get_texts(self) -> Any:
        return get_texts(self._lang)

    def _validate_not_empty(self, value: str, error_key: str) -> None:
        if not value:
            raise ValidationError(getattr(self._get_texts(), error_key))

    def _handle_compress_error(self) -> None:
        raise ConversionError(self._get_texts().error_ghostscript)

    def _handle_conversion_error(self, e: Exception) -> None:
        raise ConversionError(self._get_texts().error_convert.format(str(e))) from e

    def _validate_convert_result(self, result: ConvertResult) -> str:
        if result.success:
            if result.output_path is None:
                raise ConversionError(
                    self._get_texts().error_convert.format("Output path is None")
                )
            return result.output_path
        raise ConversionError(
            self._get_texts().error_convert.format(result.error_message)
        )

    async def _execute_with_error_handling(
        self,
        convert_fn: Callable[[], ConvertResult],
    ) -> ConvertResult:
        try:
            return await convert_fn()
        except CompressError:
            self._handle_compress_error()
        except TimeoutError as e:
            raise ConversionError(
                self._get_texts().error_convert.format(f"Timeout: {e}")
            ) from e
        except NetworkError as e:
            raise ConversionError(
                self._get_texts().error_convert.format(f"Network error: {e}")
            ) from e
        except ValidationError as e:
            raise ConversionError(
                self._get_texts().error_convert.format(f"Validation error: {e}")
            ) from e
        except ConversionError:
            raise
        except Exception as e:
            self._handle_conversion_error(e)
        raise ConversionError("Unexpected error in conversion")

    def _extract_pdf_files_from_result(self, result: WechatConvertResult) -> list[str]:
        pdf_files: list[str] = []
        for article in result.articles:
            output = article.get("output")
            if isinstance(output, str):
                pdf_files.append(output)
        return pdf_files

    def _validate_wechat_result(self, result: WechatConvertResult) -> list[str]:
        if result.success:
            pdf_files = self._extract_pdf_files_from_result(result)
            if pdf_files:
                return pdf_files
            raise WechatError("No articles found in provided WeChat URL")
        if not result.articles:
            raise WechatError("No articles found in provided WeChat URL")
        raise WechatError("Failed to convert WeChat articles")

    async def convert_html(
        self,
        url: str,
        timeout: float,
        quality: int,
    ) -> str:
        self._validate_not_empty(url, "error_no_url")

        output_path = create_output_path()

        result = await self._execute_with_error_handling(
            lambda: self._html_converter.convert(
                source=url,
                target=output_path,
                timeout=timeout,
                quality=quality,
            )
        )
        return self._validate_convert_result(result)

    async def convert_markdown(
        self,
        md_file: str,
        timeout: float,
        quality: int,
    ) -> str:
        self._validate_not_empty(md_file, "error_no_md")

        output_path = create_output_path()

        result = await self._execute_with_error_handling(
            lambda: self._markdown_converter.convert(
                source=md_file,
                target=output_path,
                timeout=timeout,
                quality=quality,
            )
        )
        return self._validate_convert_result(result)

    async def convert_html_stream(
        self,
        urls: list[str],
        timeout: float,
        quality: int,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> Generator[tuple[list[str] | None, int, int, str | None], None, None]:
        if not urls:
            raise ConversionError(self._get_texts().error_no_url)

        try:
            async for result in self._batch_converter.convert_stream(
                sources=urls,
                progress_update_fn=None,
                timeout=timeout,
                quality=quality,
            ):
                completed_files, completed_count, total_count, merge_status = result
                if progress_callback:
                    progress_callback(completed_count, total_count, "")
                yield completed_files, completed_count, total_count, merge_status
        except Exception as e:
            raise ConversionError(str(e)) from e

    async def convert_markdown_stream(
        self,
        md_files: list[str],
        timeout: float,
        quality: int,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> Generator[tuple[list[str] | None, int, int, str | None], None, None]:
        if not md_files:
            raise ConversionError(self._get_texts().error_no_md)

        try:
            async for result in self._markdown_converter.convert_stream(
                sources=md_files,
                progress_update_fn=None,
                timeout=timeout,
                quality=quality,
            ):
                completed_files, completed_count, total_count, merge_status = result
                if progress_callback:
                    progress_callback(completed_count, total_count, "")
                yield completed_files, completed_count, total_count, merge_status
        except Exception as e:
            raise ConversionError(str(e)) from e

    def _validate_wechat_url(self, url: str) -> None:
        if not url:
            raise ConversionError(self._get_texts().error_no_url)

        if "weixin.qq.com" not in url.lower():
            raise ConversionError(self._get_texts().error_invalid_wechat_url)

        if not WechatParser.is_wechat_url(url):
            raise ConversionError(f"Invalid WeChat URL: {url}")

    def is_article_list(self, url: str) -> bool:
        return self._wechat_converter.is_article_list(url)

    async def convert_wechat(
        self,
        url: str,
        timeout: float,
        quality: int,
    ) -> list[str]:
        self._validate_wechat_url(url)
        self._validate_not_empty(url, "error_no_url")

        output_dir = create_output_path()
        os.makedirs(output_dir, exist_ok=True)

        try:
            result = await self._wechat_converter.convert(
                source=url,
                target=output_dir,
                timeout=timeout,
                quality=quality,
            )
        except CompressError:
            self._handle_compress_error()
        except ConversionError:
            raise
        except Exception as e:
            self._handle_conversion_error(e)

        return self._validate_wechat_result(result)

    def convert_pdf_to_word(
        self,
        pdf_file: str,
    ) -> str:
        self._validate_not_empty(pdf_file, "error_no_pdf")

        output_path = create_output_path()

        try:
            from pdf2docx import Converter

            pdf_filename = os.path.basename(pdf_file)
            word_filename = os.path.splitext(pdf_filename)[0] + ".docx"
            word_path = os.path.join(os.path.dirname(output_path), word_filename)

            cv = Converter(pdf_file)
            cv.convert(word_path, start=0, end=None)
            cv.close()

            if os.path.exists(word_path):
                return word_path
            raise PdfToWordError("Failed to convert PDF to Word")
        except ImportError:
            raise ConversionError(
                "pdf2docx is required for PDF to Word conversion. Install with: `pip install pdf2docx`"
            )
        except PdfToWordError:
            raise
        except Exception as e:
            self._handle_conversion_error(e)
        raise ConversionError("Unexpected error in convert_pdf_to_word")

    async def convert_wechat_stream(
        self,
        url: str,
        timeout: float,
        quality: int,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> Generator[tuple[list[str] | None, int, int, str | None], None, None]:
        self._validate_wechat_url(url)
        self._validate_not_empty(url, "error_no_url")

        try:
            async for result in self._wechat_converter.convert_stream(
                sources=[url],
                progress_update_fn=None,
                timeout=timeout,
                quality=quality,
            ):
                completed_files, completed_count, total_count, merge_status = result
                if progress_callback:
                    progress_callback(completed_count, total_count, "")
                yield completed_files, completed_count, total_count, merge_status
        except Exception as e:
            raise ConversionError(str(e)) from e
