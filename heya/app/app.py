from __future__ import annotations

from PySide6.QtWidgets import QApplication

from heya.app.core.main_window import MainWindow

__all__ = ["create_app"]


def create_app(qt_app: QApplication | None = None) -> MainWindow:
    if qt_app is None:
        qt_app = QApplication.instance()
        if qt_app is None:
            qt_app = QApplication([])
            qt_app.setStyle("Fusion")

    main_window = MainWindow()
    main_window.show()
    main_window.raise_()
    main_window.activateWindow()

    return main_window
