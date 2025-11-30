"""Paragraph feature package."""

from .element import (
    DocParagraphElement,
    DocTextBlockElement,
    delete_paragraph,
    delete_paragraph_if_empty,
)

__all__ = ["DocParagraphElement", "DocTextBlockElement", "delete_paragraph", "delete_paragraph_if_empty",
           ]

