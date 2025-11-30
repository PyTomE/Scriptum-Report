"""Utilities for working with PowerPoint table shapes."""

from pptx.oxml.xmlchemy import OxmlElement

from ..base import extractFontAndDecorators


def _subElement(parent, tagname, **kwargs):
    element = OxmlElement(tagname)
    element.attrib.update(kwargs)
    existing = parent.find(element.tag)
    if existing is not None:
        parent.replace(existing, element)
    else:
        parent.append(element)
    return element


def setCellBorder(cell, border_color="FFFFFF", border_width="12700"):
    """Set the border color and width for all cell borders."""

    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()

    if isinstance(border_color, str):
        bcL = bcR = bcB = bcT = border_color
    else:
        bcL, bcR, bcB, bcT = border_color

    if not isinstance(border_width, (tuple, list)):
        bwL = bwR = bwB = bwT = border_width
    else:
        bwL, bwR, bwB, bwT = border_width

    for bel, bcol, bw in (
        ("a:lnL", bcL, str(bwL)),
        ("a:lnR", bcR, str(bwR)),
        ("a:lnB", bcB, str(bwB)),
        ("a:lnT", bcT, str(bwT)),
    ):
        if bw == 0:
            continue
        ln = _subElement(tcPr, bel, w=bw, cap="flat", cmpd="sng", algn="ctr")
        ln_solidFill = _subElement(ln, "a:solidFill")
        _subElement(ln_solidFill, "a:srgbClr", val=bcol)
        _subElement(ln, "a:prstDash", val="solid")
        _subElement(ln, "a:round")
        _subElement(ln, "a:headEnd", type="none", w="med", len="med")
        _subElement(ln, "a:tailEnd", type="none", w="med", len="med")


def get_cell_typeprops(cell):
    """Extract cell text properties if available."""

    return extractFontAndDecorators(cell.text_frame.paragraphs[0])


__all__ = ["setCellBorder", "get_cell_typeprops"]
