from __future__ import annotations

from PySide6.QtWidgets import (
    QGroupBox,
    QSlider,
    QRadioButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from heya.app.core.component import ComponentContext
from heya.app.i18n import get_texts
from heya.web.config.constants import (
    TIMEOUT_MIN,
    TIMEOUT_MAX,
    TIMEOUT_DEFAULT,
    TIMEOUT_STEP,
    QUALITY_HIGH,
    QUALITY_MEDIUM,
    QUALITY_LOW,
)

__all__ = ["SettingsPanel"]


class SettingsPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._timeout_value = TIMEOUT_DEFAULT
        self._quality_value = QUALITY_HIGH
        self._timeout_slider: QSlider | None = None
        self._quality_high: QRadioButton | None = None
        self._quality_medium: QRadioButton | None = None
        self._quality_low: QRadioButton | None = None
        self._timeout_label: QLabel | None = None

    def render(self, ctx: ComponentContext, parent: QWidget | None = None) -> QWidget:
        texts = get_texts(ctx.lang)

        group_box = QGroupBox(f"⚙️ {texts.settings_label}", parent)
        layout = QVBoxLayout()

        timeout_layout = QHBoxLayout()
        timeout_label = QLabel(texts.timeout_label)
        timeout_label.setMinimumWidth(100)
        timeout_value_label = QLabel(str(self._timeout_value))
        timeout_value_label.setMinimumWidth(50)

        timeout_slider = QSlider(Qt.Orientation.Horizontal)
        timeout_slider.setMinimum(TIMEOUT_MIN)
        timeout_slider.setMaximum(TIMEOUT_MAX)
        timeout_slider.setValue(self._timeout_value)
        timeout_slider.setSingleStep(TIMEOUT_STEP)
        timeout_slider.valueChanged.connect(
            lambda v: timeout_value_label.setText(str(v))
        )
        timeout_slider.valueChanged.connect(self._set_timeout)

        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(timeout_slider)
        timeout_layout.addWidget(timeout_value_label)

        quality_layout = QVBoxLayout()
        quality_label = QLabel(texts.compression_level)
        quality_info = QLabel(texts.compression_info)
        quality_info.setStyleSheet("color: gray; font-size: 10px;")

        quality_high = QRadioButton(texts.quality_high)
        quality_medium = QRadioButton(texts.quality_medium)
        quality_low = QRadioButton(texts.quality_low)

        quality_high.setChecked(self._quality_value == QUALITY_HIGH)
        quality_medium.setChecked(self._quality_value == QUALITY_MEDIUM)
        quality_low.setChecked(self._quality_value == QUALITY_LOW)

        quality_high.toggled.connect(lambda checked: checked and self._set_quality(QUALITY_HIGH))
        quality_medium.toggled.connect(lambda checked: checked and self._set_quality(QUALITY_MEDIUM))
        quality_low.toggled.connect(lambda checked: checked and self._set_quality(QUALITY_LOW))

        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(quality_high)
        quality_layout.addWidget(quality_medium)
        quality_layout.addWidget(quality_low)
        quality_layout.addWidget(quality_info)

        layout.addLayout(timeout_layout)
        layout.addLayout(quality_layout)

        group_box.setLayout(layout)

        self._timeout_slider = timeout_slider
        self._quality_high = quality_high
        self._quality_medium = quality_medium
        self._quality_low = quality_low
        self._timeout_label = timeout_value_label

        return group_box

    def _set_timeout(self, value: int) -> None:
        self._timeout_value = value

    def _set_quality(self, value: int) -> None:
        self._quality_value = value

    @property
    def timeout(self) -> int:
        return self._timeout_value

    @property
    def quality(self) -> int:
        return self._quality_value

    def set_timeout(self, value: int) -> None:
        self._timeout_value = value
        if self._timeout_slider:
            self._timeout_slider.setValue(value)
        if self._timeout_label:
            self._timeout_label.setText(str(value))

    def set_quality(self, value: int) -> None:
        self._quality_value = value
        if self._quality_high:
            self._quality_high.setChecked(value == QUALITY_HIGH)
        if self._quality_medium:
            self._quality_medium.setChecked(value == QUALITY_MEDIUM)
        if self._quality_low:
            self._quality_low.setChecked(value == QUALITY_LOW)
