"""Table feature package."""

from typing import TYPE_CHECKING

from .element import PptTableElement
from .utils import get_cell_typeprops, setCellBorder

__all__ = ["PptTableElement", "TableTemplate", "get_cell_typeprops", "setCellBorder"]

# work around a getShapes circular import
if TYPE_CHECKING:  # pragma: no cover
    from .template import TableTemplate


def __getattr__(name):
    if name == "TableTemplate":
        from .template import TableTemplate as _TableTemplate

        return _TableTemplate
    raise AttributeError(f"module {__name__} has no attribute {name!r}")
