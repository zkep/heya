from __future__ import annotations

import os

from heya.core.models import PdfContent

__all__ = ["PdfWriter"]


class PdfWriter:
    def write(self, content: PdfContent, target: str) -> None:
        target = os.path.abspath(target)
        target_dir = os.path.dirname(target)
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
        with open(target, "wb") as f:
            f.write(content.data)
