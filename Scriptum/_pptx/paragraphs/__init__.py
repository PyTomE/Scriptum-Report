"""Paragraph feature package."""

from typing import TYPE_CHECKING

from .element import PptParagraphElement, PptTextElement

__all__ = ["PptParagraphElement", "PptTextElement", "TextTemplate"]

# work around a getShapes circular import
if TYPE_CHECKING:  # pragma: no cover
    from .template import TextTemplate


def __getattr__(name):
    if name == "TextTemplate":
        from .template import TextTemplate as _TextTemplate

        return _TextTemplate
    raise AttributeError(f"module {__name__} has no attribute {name!r}")
