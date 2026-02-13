from __future__ import annotations

import gradio as gr

from heya.web.core.component import ComponentContext
from heya.web.i18n import get_texts
from heya.web.constants import (
    TIMEOUT_MIN,
    TIMEOUT_MAX,
    TIMEOUT_DEFAULT,
    TIMEOUT_STEP,
    QUALITY_HIGH,
    QUALITY_MEDIUM,
    QUALITY_LOW,
)

__all__ = ["SettingsPanel"]


class SettingsPanel:
    """Reusable settings panel with timeout and quality controls."""

    def __init__(self, open_by_default: bool = False) -> None:
        """Initialize settings panel.

        Args:
            open_by_default: Whether the accordion is open by default
        """
        self._open_by_default = open_by_default
        self._timeout: gr.Slider | None = None
        self._quality: gr.Radio | None = None
        self._accordion: gr.Accordion | None = None

    def render(self, ctx: ComponentContext) -> tuple[gr.Accordion, gr.Slider, gr.Radio]:
        """Render the settings panel.

        Args:
            ctx: Component context

        Returns:
            Tuple of accordion, timeout slider, and quality radio
        """
        texts = get_texts(ctx.lang)
        settings_accordion = gr.Accordion(
            f"⚙️ {texts.settings_label}",
            open=self._open_by_default,
        )
        with settings_accordion:
            with gr.Row():
                with gr.Column(scale=1):
                    timeout = gr.Slider(
                        minimum=TIMEOUT_MIN,
                        maximum=TIMEOUT_MAX,
                        value=TIMEOUT_DEFAULT,
                        step=TIMEOUT_STEP,
                        label=texts.timeout_label,
                    )
                with gr.Column(scale=1):
                    quality_radio = gr.Radio(
                        choices=[
                            (texts.quality_high, QUALITY_HIGH),
                            (texts.quality_medium, QUALITY_MEDIUM),
                            (texts.quality_low, QUALITY_LOW),
                        ],
                        value=QUALITY_HIGH,
                        label=texts.compression_level,
                        info=texts.compression_info,
                    )

        self._timeout = timeout
        self._quality = quality_radio
        self._accordion = settings_accordion
        return settings_accordion, timeout, quality_radio

    @property
    def timeout(self) -> gr.Slider:
        """Get the timeout slider component."""
        if self._timeout is None:
            raise RuntimeError("Settings panel not rendered yet")
        return self._timeout

    @property
    def quality(self) -> gr.Radio:
        """Get the quality radio component."""
        if self._quality is None:
            raise RuntimeError("Settings panel not rendered yet")
        return self._quality

    @property
    def accordion(self) -> gr.Accordion:
        """Get the accordion component."""
        if self._accordion is None:
            raise RuntimeError("Settings panel not rendered yet")
        return self._accordion
