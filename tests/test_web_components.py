from __future__ import annotations

import pytest

from heya.web.components.converter import (
    HtmlConverterComponent,
    MarkdownConverterComponent,
)
from heya.web.components.settings import SettingsComponent
from heya.web.components.tips import TipsComponent
from heya.web.core.component import ComponentContext
from heya.web.core.registry import ComponentRegistry


class TestComponentRegistry:
    def test_register_component(self):
        registry = ComponentRegistry()
        component = TipsComponent()
        registry.register(component)
        assert "tips" in registry
        assert len(registry) == 1

    def test_unregister_component(self):
        registry = ComponentRegistry()
        component = TipsComponent()
        registry.register(component)
        registry.unregister("tips")
        assert "tips" not in registry
        assert len(registry) == 0

    def test_get_component(self):
        registry = ComponentRegistry()
        component = TipsComponent()
        registry.register(component)
        assert registry.get("tips") is component
        assert registry.get("nonexistent") is None

    def test_iterate_components(self):
        registry = ComponentRegistry()
        registry.register(TipsComponent())
        registry.register(SettingsComponent())
        names = [c.name for c in registry]
        assert "tips" in names
        assert "settings" in names


class TestComponentContext:
    def test_default_context(self):
        ctx = ComponentContext()
        assert ctx.lang == "zh"
        assert ctx.data == {}

    def test_custom_context(self):
        ctx = ComponentContext(lang="en", data={"key": "value"})
        assert ctx.lang == "en"
        assert ctx.data == {"key": "value"}


class TestTipsComponent:
    def test_component_name(self):
        component = TipsComponent()
        assert component.name == "tips"

    def test_get_i18n_keys(self):
        component = TipsComponent()
        keys = component.get_i18n_keys()
        assert isinstance(keys, dict)


class TestSettingsComponent:
    def test_component_name(self):
        component = SettingsComponent()
        assert component.name == "settings"


class TestHtmlConverterComponent:
    def test_component_name(self):
        component = HtmlConverterComponent()
        assert component.name == "html_converter"


class TestMarkdownConverterComponent:
    def test_component_name(self):
        component = MarkdownConverterComponent()
        assert component.name == "markdown_converter"
