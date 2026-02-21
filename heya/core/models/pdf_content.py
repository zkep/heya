from __future__ import annotations

from dataclasses import dataclass

__all__ = ["PdfContent"]


@dataclass(frozen=True)
class PdfContent:
    data: bytes

    def __post_init__(self) -> None:
        if not isinstance(self.data, bytes):
            raise TypeError("PDF content must be bytes")

    def __len__(self) -> int:
        return len(self.data)

    @property
    def size(self) -> int:
        return len(self.data)

    @property
    def size_kb(self) -> float:
        return len(self.data) / 1024

    @property
    def size_mb(self) -> float:
        return len(self.data) / (1024 * 1024)
