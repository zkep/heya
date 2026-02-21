from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

from heya.core.logging import format_error_with_issue, get_logger

__all__ = ["PdfMerger", "PdfMergeItem"]

logger = get_logger(__name__)


@dataclass
class PdfMergeItem:
    title: str
    file_path: str
    page_number: int = 0


class PdfMerger:
    _chinese_font_registered = False
    _chinese_font_name = None

    @classmethod
    def _register_chinese_font(cls) -> bool:
        """Register Chinese font with fallback mechanism for cross-platform support"""
        if cls._chinese_font_registered:
            return cls._chinese_font_name is not None

        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import platform

        # Define font paths for different platforms
        font_candidates = []

        system = platform.system()

        if system == "Darwin":  # macOS
            font_candidates = [
                ("Heiti SC", "/System/Library/Fonts/STHeiti Medium.ttc"),
                ("Heiti TC", "/System/Library/Fonts/STHeiti Medium.ttc"),
                ("PingFang SC", "/System/Library/Fonts/PingFang.ttc"),
                ("Hiragino Sans GB", "/System/Library/Fonts/Hiragino Sans GB.ttc"),
                ("Songti SC", "/System/Library/Fonts/Supplemental/Songti.ttc"),
                ("Arial Unicode MS", "/Library/Fonts/Arial Unicode.ttf"),
            ]
        elif system == "Windows":  # Windows
            font_candidates = [
                ("SimHei", "C:/Windows/Fonts/simhei.ttf"),
                ("SimSun", "C:/Windows/Fonts/simsun.ttc"),
                ("Microsoft YaHei", "C:/Windows/Fonts/msyh.ttc"),
                ("Microsoft YaHei UI", "C:/Windows/Fonts/msyh.ttc"),
                ("KaiTi", "C:/Windows/Fonts/simkai.ttf"),
            ]
        elif system == "Linux":  # Linux
            font_candidates = [
                (
                    "WenQuanYi Micro Hei",
                    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                ),
                ("WenQuanYi Zen Hei", "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
                (
                    "Noto Sans CJK SC",
                    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
                ),
                (
                    "Droid Sans Fallback",
                    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
                ),
            ]

        # Try to register fonts in order of preference
        for font_name, font_path in font_candidates:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
                    cls._chinese_font_name = "ChineseFont"
                    cls._chinese_font_registered = True
                    return True
                except Exception:
                    continue

        cls._chinese_font_registered = True
        return False

    @classmethod
    def _get_chinese_font_name(cls) -> str:
        """Get the Chinese font name or fallback"""
        if not cls._chinese_font_registered:
            cls._register_chinese_font()
        return cls._chinese_font_name if cls._chinese_font_name else "Helvetica"

    def merge_pdfs_with_toc(
        self,
        items: list[PdfMergeItem],
        output_path: str,
        title: str = "documents",
    ) -> str:
        try:
            from pypdf import PdfReader, PdfWriter as PyPdfWriter

            writer = PyPdfWriter()

            page_offset = 0
            toc_items: list[tuple[str, int]] = []

            for item in items:
                if not os.path.exists(item.file_path):
                    continue

                reader = PdfReader(item.file_path)
                item.page_number = page_offset + 1

                for page in reader.pages:
                    writer.add_page(page)

                page_offset += len(reader.pages)
                toc_items.append((item.title, item.page_number))

            if not toc_items:
                raise ValueError("No valid PDF files to merge")

            toc_pdf = self._create_toc_pdf(toc_items, title)
            toc_reader = PdfReader(toc_pdf)

            toc_page_count = len(toc_reader.pages)
            for i, page in enumerate(toc_reader.pages):
                writer.insert_page(page, index=i)

            try:
                root_bookmark = writer.add_outline_item(title, 0)
                for idx, (item_title, page_num) in enumerate(toc_items, 1):
                    writer.add_outline_item(
                        f"{idx}. {item_title}",
                        page_num + toc_page_count - 1,
                        parent=root_bookmark,
                    )
            except Exception:
                pass

            output_path = os.path.abspath(output_path)
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            with open(output_path, "wb") as f:
                writer.write(f)

            os.unlink(toc_pdf)

            return output_path

        except ImportError as e:
            raise ImportError(
                "reportlab is required for PDF merging with TOC. "
                "Install with: pip install reportlab"
            ) from e
        except Exception as e:
            raise Exception(format_error_with_issue(e)) from e

    def _create_toc_pdf(self, toc_items: list[tuple[str, int]], title: str) -> str:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
        )

        import tempfile

        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        temp_path = temp_file.name
        temp_file.close()

        # Register Chinese font using cross-platform detection
        font_name = self._get_chinese_font_name()

        doc = SimpleDocTemplate(
            temp_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        styles = getSampleStyleSheet()

        # Create styles with Chinese font if registered
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=30,
            alignment=1,
            fontName=font_name,
        )

        heading_style = ParagraphStyle(
            "TOCHeading",
            parent=styles["Heading2"],
            fontSize=16,
            spaceAfter=12,
            fontName=font_name,
        )

        normal_style = ParagraphStyle(
            "Normal",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=12,
        )

        story: list[Any] = []

        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("目录", heading_style))
        story.append(Spacer(1, 0.1 * inch))

        # Create TOC data with Paragraph objects for proper Chinese character rendering
        toc_data = [
            [
                Paragraph("序号", normal_style),
                Paragraph("标题", normal_style),
                Paragraph("页码", normal_style),
            ]
        ]
        for idx, (item_title, page_num) in enumerate(toc_items, 1):
            # Wrap text in Paragraph objects for proper Chinese character rendering
            toc_data.append(
                [
                    Paragraph(str(idx), normal_style),
                    Paragraph(item_title, normal_style),
                    Paragraph(str(page_num), normal_style),
                ]
            )

        toc_table = Table(toc_data, colWidths=[0.5 * inch, 4.5 * inch, 1 * inch])
        toc_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), "#E0E0E0"),
                    ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (2, 0), (2, -1), "CENTER"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), "#FFFFFF"),
                    ("GRID", (0, 0), (-1, -1), 0.5, "#CCCCCC"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), ["#F9F9F9", "#FFFFFF"]),
                ]
            )
        )

        story.append(toc_table)

        doc.build(story)

        return temp_path

    def merge_pdfs_simple(self, files: list[str], output_path: str) -> str:
        try:
            from pypdf import PdfReader, PdfWriter as PyPdfWriter

            writer = PyPdfWriter()

            for file_path in files:
                if not os.path.exists(file_path):
                    continue

                reader = PdfReader(file_path)
                for page in reader.pages:
                    writer.add_page(page)

            output_path = os.path.abspath(output_path)
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            with open(output_path, "wb") as f:
                writer.write(f)

            return output_path

        except Exception as e:
            raise Exception(format_error_with_issue(e)) from e

    def merge_pdfs_with_options(
        self,
        pdf_files: list[str],
        merge_title: str = "documents",
        output_path: str | None = None,
        filename_prefix: str = "merged",
        output_dir: str | None = None,
    ) -> str:
        """Merge multiple PDF files into a single PDF with table of contents.

        This is a convenience method that handles file validation, item creation,
        and output path generation automatically.

        Args:
            pdf_files: List of PDF file paths to merge
            merge_title: Title for the merged PDF and TOC
            output_path: Optional custom output path. If not provided, one will be generated
            filename_prefix: Prefix for auto-generated output filename
            output_dir: Directory for output file. If not provided, uses temp directory

        Returns:
            Path to the merged PDF file

        Raises:
            ValueError: If no valid PDF files to merge
            Exception: If merge operation fails
        """
        if not pdf_files or len(pdf_files) == 0:
            raise ValueError("No PDF files provided for merging")

        merge_items: list[PdfMergeItem] = []
        for pdf_path in pdf_files:
            if os.path.exists(pdf_path):
                filename = os.path.basename(pdf_path)
                title = os.path.splitext(filename)[0]
                merge_items.append(PdfMergeItem(title=title, file_path=pdf_path))

        if not merge_items:
            raise ValueError("No valid PDF files found to merge")

        if output_path is None:
            if output_dir is None:
                from heya.core.temp import create_output_path
                output_dir = create_output_path()
            
            os.makedirs(output_dir, exist_ok=True)
            timestamp = int(time.time())
            merged_filename = f"{filename_prefix}_{timestamp}.pdf"
            output_path = os.path.join(output_dir, merged_filename)

        return self.merge_pdfs_with_toc(
            items=merge_items,
            output_path=output_path,
            title=merge_title,
        )
