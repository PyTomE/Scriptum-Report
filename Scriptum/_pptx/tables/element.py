"""Table element helpers."""

from ...element import TableElement
from ..base import PptElement


class PptTableElement(PptElement, TableElement):
    """Tables and table placeholders."""

    def __init__(self, elem, tags):
        super().__init__(elem)
        self.tags = tags
        self.type = "table"
