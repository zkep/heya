from __future__ import annotations

import os
from collections.abc import Callable
from typing import TYPE_CHECKING, Generator

from heya.core.helpers import convert, convert_md
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
from heya.web.i18n import get_texts

if TYPE_CHECKING:
    from typing import Any

__all__ = ["WebConvertService", "ConversionError"]


class ConversionError(Exception):
    pass


def _convert_core_result_to_gradio(
    completed_files: list[str] | None,
    completed_count: int,
    total_count: int,
    merge_status: str | None,
    progress_update_fn: Callable[[int, int, str], dict[str, Any]] | None = None,
    lang: str = "zh",
) -> tuple[list[str] | None, dict[str, Any], dict[str, Any]]:
    try:
        import gradio as gr
        HAS_GRADIO = True
    except ImportError:
        HAS_GRADIO = False
    
    progress_update = {}
    button_update = {}
    
    if HAS_GRADIO:
        is_complete = completed_count == total_count and completed_count > 0
        
        if progress_update_fn and not is_complete:
            progress_update = progress_update_fn(completed_count, total_count, "")
        elif is_complete:
            from heya.web.i18n import get_texts
            texts = get_texts(lang)
            progress_update = gr.update(interactive=True, value=texts.convert_btn)
        else:
            progress_update = gr.update(interactive=False)
        
        show_merge_button = merge_status == "completed"
        button_update = gr.update(visible=show_merge_button)
    
    return (
        completed_files.copy() if completed_files else None,
        progress_update,
        button_update,
    )


class WebConvertService:
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
        from heya.core.wechat.converter_factory import create_wechat_converter

        self._wechat_converter = create_wechat_converter(compress=True)
        self._wechat_stream_converter = WechatConverter(
            html_converter=create_wechat_converter(compress=True)._html_converter
        )
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

    def _execute_with_error_handling(
        self,
        convert_fn: Callable[[], ConvertResult],
    ) -> ConvertResult:
        try:
            return convert_fn()
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

        try:
            result = await self._html_converter.convert(
                source=url,
                target=output_path,
                timeout=timeout,
                quality=quality,
            )
        except Exception as e:
            raise ConversionError(str(e)) from e
        return self._validate_convert_result(result)

    def convert_markdown(
        self,
        md_file: str,
        timeout: float,
        quality: int,
    ) -> str:
        self._validate_not_empty(md_file, "error_no_md")

        output_path = create_output_path()

        result = self._execute_with_error_handling(
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
        lang: str,
        progress_update_fn: Callable[[int, int, str], dict[str, Any]] | None = None,
    ) -> Generator[tuple[list[str] | None, dict[str, Any], dict[str, Any]], None, None]:
        if not urls:
            raise ConversionError(self._get_texts().error_no_url)

        try:
            stream = self._batch_converter.convert_stream(
                sources=urls,
                progress_update_fn=None,
                timeout=timeout,
                quality=quality,
            )
            async for result in stream:
                completed_files, completed_count, total_count, merge_status = result
                yield _convert_core_result_to_gradio(
                    completed_files, completed_count, total_count, merge_status, progress_update_fn, lang
                )
        except Exception as e:
            raise ConversionError(str(e)) from e

    async def convert_markdown_stream(
        self,
        md_files: list[str],
        timeout: float,
        quality: int,
        lang: str,
        progress_update_fn: Callable[[int, int, str], dict[str, Any]] | None = None,
    ) -> Generator[tuple[list[str] | None, dict[str, Any], dict[str, Any]], None, None]:
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
                yield _convert_core_result_to_gradio(
                    completed_files, completed_count, total_count, merge_status, progress_update_fn, lang
                )
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

    def convert_wechat(
        self,
        url: str,
        timeout: float,
        quality: int,
    ) -> list[str]:
        import asyncio

        self._validate_wechat_url(url)
        self._validate_not_empty(url, "error_no_url")

        output_dir = create_output_path()
        os.makedirs(output_dir, exist_ok=True)

        try:
            result = asyncio.run(
                self._wechat_converter.convert(
                    source=url,
                    target=output_dir,
                    timeout=timeout,
                    quality=quality,
                )
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
        lang: str,
        progress_update_fn: Callable[[int, int, str], dict[str, Any]] | None = None,
    ) -> Generator[tuple[list[str] | None, dict[str, Any], dict[str, Any]], None, None]:
        self._validate_wechat_url(url)
        self._validate_not_empty(url, "error_no_url")

        try:
            async for result in self._wechat_stream_converter.convert_stream(
                sources=[url],
                progress_update_fn=progress_update_fn,
                timeout=timeout,
                quality=quality,
            ):
                completed_files, completed_count, total_count, merge_status = result
                yield _convert_core_result_to_gradio(
                    completed_files, completed_count, total_count, merge_status, progress_update_fn, lang
                )
        except Exception as e:
            raise ConversionError(str(e)) from e
