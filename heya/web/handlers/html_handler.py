from __future__ import annotations

from heya.web.handlers.base_handler import BaseHandler, HandlerResponse

__all__ = ["HtmlHandler"]


class HtmlHandler(BaseHandler):
    def convert_with_error_handling(
        self,
        url: str,
        timeout: float,
        quality: int,
        lang: str,
    ) -> HandlerResponse:
        try:
            service = self._get_service(lang)
            result = service.convert_html(url, timeout, quality)
            return self._get_success_response(result, lang)
        except Exception as e:
            return self._handle_conversion_error(e, lang)
