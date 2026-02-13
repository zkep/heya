from __future__ import annotations

from typing import Any

from heya.web.core.component import Component

__all__ = ["ComponentRegistry"]


class ComponentRegistry:
    def __init__(self) -> None:
        self._components: dict[str, Component] = {}

    def register(self, component: Component) -> None:
        self._components[component.name] = component

    def unregister(self, name: str) -> None:
        self._components.pop(name, None)

    def get(self, name: str) -> Component | None:
        return self._components.get(name)

    def get_all(self) -> list[Component]:
        return list(self._components.values())

    def get_all_i18n_keys(self) -> dict[str, dict[str, dict[str, str]]]:
        result: dict[str, dict[str, dict[str, str]]] = {}
        for component in self._components.values():
            for lang, keys in component.get_i18n_keys().items():
                if lang not in result:
                    result[lang] = {}
                result[lang][component.name] = keys
        return result

    def render_all(self, app: Any, lang: str) -> dict[str, Any]:
        from heya.web.core.component import ComponentContext

        ctx = ComponentContext(lang=lang)
        outputs: dict[str, Any] = {}
        for component in self._components.values():
            outputs[component.name] = component.render(ctx)
            component.register_handlers(app)
        return outputs

    def __contains__(self, name: str) -> bool:
        return name in self._components

    def __iter__(self):
        return iter(self._components.values())

    def __len__(self) -> int:
        return len(self._components)
