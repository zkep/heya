from __future__ import annotations

from heya.core.template.html_template import DEFAULT_CSS, HTML_TEMPLATE, render_html


class TestRenderHtml:
    def test_basic_render(self):
        html = render_html("Test Title", "<p>Content</p>")
        assert "Test Title" in html
        assert "<p>Content</p>" in html
        assert "<!DOCTYPE html>" in html

    def test_custom_css(self):
        custom_css = "body { color: red; }"
        html = render_html("Title", "Content", css=custom_css)
        assert custom_css in html

    def test_default_css_used(self):
        html = render_html("Title", "Content")
        assert DEFAULT_CSS in html


class TestTemplates:
    def test_html_template_has_placeholders(self):
        assert "{title}" in HTML_TEMPLATE
        assert "{css}" in HTML_TEMPLATE
        assert "{content}" in HTML_TEMPLATE

    def test_default_css_not_empty(self):
        assert len(DEFAULT_CSS) > 0
        assert "body" in DEFAULT_CSS
