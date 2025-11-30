"""Table template helpers."""

from copy import deepcopy

from .element import PptTableElement
from ..paragraphs import PptTextElement
from ..template_utils import (
    compute_template_bounds,
    resolve_template_box,
)
from ...tag.tag import getReTag, createTag
from ...element.base import replaceTextInRuns

debug = True


class TableTemplate:
    """Template to duplicate a table placeholder."""

    def __init__(self, shapes):
        
        self.elements = shapes

        bounds = compute_template_bounds(shapes)
        self.top = bounds.top
        self.left = bounds.left
        self.width = bounds.width
        self.height = bounds.height

        for element in self.elements:
            element.storeAttributes()
            # make relative to the template
            # most upper and most left elements are "0"
            element.attrs.top -= self.top
            element.attrs.left -= self.left


    def copyAndFill(self, slide, baseshape, value, actions) -> None:
        """do the full copy and fill operation
        this will return nothing as it fills all content

        slide - the slide to place content on
        baseshape - the shape that defines the size 
        actions - defined actions from rdf that may modify positions or contain more
        value - the main value object, here a table-value
        """

        box = resolve_template_box(
            baseshape,
            self.width,
            self.height,
            actions,
            default_width="available",
            default_height="available",
        )

        value.load()
        if not value.object.exists:
            # need to define the fail action
            warning = f"non existing table file {value.object.filename!r}"
            rows = 2
            columns = 2
        else:
            warning = False
            rows = value.object.content.rows
            columns = value.object.content.cols

        for element in self.elements:
            attrs = element.attrs

            element_top = int(box.top) + attrs.top
            element_left = int(box.left) + attrs.left
            element_width = min(attrs.width, box.width)
            element_height = min(attrs.height, box.height)

            if element.type == "table":
                shape = slide.shapes.add_table(
                    rows, columns, element_left, element_top, element_width, element_height
                )
                
                new_element = PptTableElement(shape, deepcopy(element.tags))
                if not warning:
                    value.object.fill(new_element)
                else:
                    # a pure warning on top?
                    text_shape = slide.shapes.add_textbox(
                        element_left, element_top, element_width, element_height
                    )
                    text_shape.text_frame.paragraphs[0].text = warning

                attrs.setTableAttrs(shape.table)
            else:
                shape = slide.shapes.add_textbox(
                    element_left, element_top, element_width, element_height
                )
                copiedtags = deepcopy(element.tags)
                text_frame = shape.text_frame
                text_frame.paragraphs[0].text = element.thing.text_frame.text

                if copiedtags[0].child:
                    oldre = getReTag(copiedtags[0])
                    newtag = createTag(copiedtags[0].child)
                    if copiedtags[0].child in actions and not warning:
                        replacestring = value.object.content.caption
                    else:
                        replacestring = newtag.rawtag
                    #print('NNN',newtag.printable)
                    replaceTextInRuns(
                        text_frame.paragraphs[0].runs, shape.text, oldre, replacestring
                    )
                    copiedtags[0] = newtag

                new_element = PptTextElement(shape, copiedtags)
                #print('AAA',actions, type(actions['description'].object))
                attrs.setFontAttrs(text_frame)

# a:tbl/a:tblPr/a:tableStyleId


    
