from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

__all__ = ["UITexts", "I18nManager", "get_texts", "LANGUAGE_OPTIONS"]


@dataclass
class UITexts:
    title: str
    subtitle: str
    html_tab: str
    md_tab: str
    wechat_tab: str
    pdf_to_word_tab: str
    url_label: str
    url_placeholder: str
    wechat_url_label: str
    wechat_url_placeholder: str
    md_file_label: str
    pdf_file_label: str
    output_label: str
    wechat_output_label: str
    word_output_label: str
    convert_btn: str
    convert_word_btn: str
    timeout_label: str
    compress_label: str
    compression_level: str
    compression_info: str
    compress_warning: str
    tips_title: str
    tips_html: str
    tips_md: str
    tips_wechat: str
    tips_pdf_to_word: str
    tips_compress: str
    error_no_url: str
    error_no_md: str
    error_no_pdf: str
    error_convert: str
    error_invalid_wechat_url: str
    error_ghostscript: str
    error_no_files_to_merge: str
    error_title: str
    error_report_btn: str
    error_cancel_btn: str
    starting_server: str
    convert_success: str
    filename: str
    filesize: str
    source: str
    source_md: str
    source_pdf: str
    download_ready: str
    settings_label: str
    quality_high: str
    quality_medium: str
    quality_low: str
    merge_btn: str
    merged_pdf_label: str
    upload_drag_text: str
    upload_or_text: str
    upload_click_text: str


LANGUAGE_OPTIONS = [
    ("🇨🇳 中", "zh"),
    ("🇺🇸 En", "en"),
    ("🇰🇷 한", "ko"),
]


class I18nManager:
    def __init__(self, default_lang: str = "zh") -> None:
        self.default_lang = default_lang
        self._texts_cache: dict[str, UITexts] = {}
        self._locales_dir = os.path.join(os.path.dirname(__file__), "locales")

    def get_texts(self, lang: str) -> UITexts:
        if lang in self._texts_cache:
            return self._texts_cache[lang]

        translation = self._load_translation(lang)
        texts = UITexts(**translation)
        self._texts_cache[lang] = texts
        return texts

    def _load_translation(self, lang: str) -> dict[str, Any]:
        json_path = os.path.join(self._locales_dir, f"{lang}.json")

        if os.path.exists(json_path):
            try:
                import json

                with open(json_path, encoding="utf-8") as f:
                    result: dict[str, Any] = json.load(f)
                    return result
            except Exception:
                pass

        return self._load_translation(self.default_lang)

    def load_from_yaml(self, yaml_path: str) -> None:
        if not os.path.exists(yaml_path):
            return

        try:
            import yaml
        except ImportError:
            return
        try:
            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and isinstance(data, dict):
                    for lang, texts in data.items():
                        if isinstance(texts, dict):
                            self._texts_cache.pop(lang, None)
        except Exception:
            pass


_i18n_manager = I18nManager()


def get_texts(lang: str) -> UITexts:
    return _i18n_manager.get_texts(lang)
