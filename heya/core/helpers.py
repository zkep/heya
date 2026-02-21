from __future__ import annotations

from heya.core.converters import create_html_converter
from heya.core.markdown import create_markdown_converter
from heya.core.wechat import create_wechat_converter
from heya.core.pdf import convert_pdf_to_word

__all__ = [
    "convert",
    "convert_md",
    "convert_wechat",
    "convert_pdf_to_word",
]

convert = create_html_converter()
convert_md = create_markdown_converter()


async def convert_wechat(
    url: str,
    output_dir: str,
    timeout: float = 3.0,
    compress: bool = False,
    quality: int = 0,
):
    converter = create_wechat_converter(timeout, compress)
    return await converter.convert(
        url=url,
        output_dir=output_dir,
        timeout=timeout,
        compress=compress,
        quality=quality,
    )
