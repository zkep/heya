#!/usr/bin/env python3
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from heya.app import create_app


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    main_window = create_app()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
