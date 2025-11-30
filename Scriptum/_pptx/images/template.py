"""Image template handling."""

from copy import deepcopy

from ..paragraphs import PptTextElement
from ..units import units
from ..template_utils import (
    compute_template_bounds,
    float_from_actions,
    resolve_template_box,
    scale_dimension,
)

from ...tag.tag import getReTag, createTag
from ...element.base import replaceTextInRuns

debug = False

class ImageTemplate:
    """A template describing how to duplicate image groups.
    where the shapes could be either a list with 
    - a single shape
    - multiple shapes
    groupshapes do not exist anymore on this level, so we have to compute overall
    top, left, width, height from all shapes
    """

    def __init__(self, shapes):

        self.elements = shapes

        bounds = compute_template_bounds(shapes)
        self.top = bounds.top
        self.left = bounds.left
        self.width = bounds.width
        self.height = bounds.height

        if debug:
            print(
                "calculated sizes in template:",
                self.top,
                self.left,
                self.width,
                self.height,
            )

        for i, element in enumerate(self.elements):
            element.storeAttributes()

            if debug:
                print(
                    f"old relative position for element ({i}): {element.attrs.top} {element.attrs.left}"
                )

            # make relative to the template
            # most upper and most left elements are "0"
            element.attrs.top -= self.top
            element.attrs.left -= self.left

            if debug:
                print(
                    f"new relative position for element ({i}): {element.attrs.top} {element.attrs.left}"
                )

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

        scale = float_from_actions(actions, "scale")
        if not scale or scale <= 0:
            scale = 1.0

        value.load()

        if not value.object.exists:
            # need to define the fail action
            warning = f"non existing image file {value.object.filename!r}"
        else:
            warning = False

        for element in self.elements:
            attrs = element.attrs

            element_top = int(box.top) + attrs.top
            element_left = int(box.left) + attrs.left

            if element.type == "image":
                if not warning:
                    # scale the shape such that the image follows
                    # account for offset in both directions
                    element_width = scale_dimension(box.width-attrs.left, scale)
                    element_height = scale_dimension(box.height-attrs.top, scale)

                    #print('V',element_width, element_height, scale)
                    img_width, img_height = self._resolve_image_geometry(
                        value.object, element_width, element_height
                        )
                    #print('N', img_width, img_height)
                    slide.shapes.add_picture(
                        value.object.filename,
                        top=element_top,
                        left=element_left,
                        width=img_width,
                        height=img_height,
                        )
                else:
                    # a pure warning on top?
                    shape = slide.shapes.add_textbox(
                        element_left, element_top, attrs.width, attrs.height
                    )
                    shape.text_frame.paragraphs[0].text = warning
  
            else:

                shape = slide.shapes.add_textbox(
                    element_left, element_top, attrs.width, attrs.height
                )
                copiedtags = deepcopy(element.tags)
                text_frame = shape.text_frame
                text_frame.paragraphs[0].text = element.thing.text_frame.text

                if copiedtags[0].child:
                    oldre = getReTag(copiedtags[0])
                    newtag = createTag(copiedtags[0].child)
                    #print('AAA', actions, newtag, copiedtags[0].child)
                    if copiedtags[0].child in actions and not warning:
                        replacestring = str(actions[copiedtags[0].child])
                    else:
                        replacestring = newtag.rawtag
                    replaceTextInRuns(
                        text_frame.paragraphs[0].runs, shape.text, oldre, replacestring
                    )
                    copiedtags[0] = newtag

                new_element = PptTextElement(shape, copiedtags)
                attrs.setFontAttrs(text_frame)

    def _resolve_image_geometry(self, image, max_width: int, max_height: int) -> tuple[int, int]:
        """extract the final size of the image
        max_width, max_height are the dimensions of the target region"""

        image.content
        natural_width = units["pt"](image.width)
        natural_height = units["pt"](image.height)
        #print('Nat', natural_width, natural_height, image.width, image.height)

        # is that possible?
        if natural_width == 0 or natural_height == 0:
            return max_width, max_height

        ratio = natural_width / natural_height
        #print('Rat', ratio)

        # what is possible
        width = min(natural_width, max_width)
        height = width / ratio

        if height > max_height:
            height = max_height
            width = height * ratio

        width = min(width, max_width)
        height = min(height, max_height)

        return int(round(width)), int(round(height))

class AnimationTemplate(ImageTemplate):
    
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

        scale = float_from_actions(actions, "scale")
        if not scale or scale <= 0:
            scale = 1.0

        value.load()

        if not value.object.exists:
            # need to define the fail action
            warning = f"non existing video file {value.object.filename!r}"
        else:
            warning = False
            posterimage = actions.get("image:poster") or actions.get("image")
            #print('PO',actions, type(posterimage))

        for element in self.elements:
            attrs = element.attrs

            element_top = int(box.top) + attrs.top
            element_left = int(box.left) + attrs.left
            
            if element.type == "image":
                if not warning:
                    # scale the shape such that the image follows
                    # account for offset in both directions
                    element_width = scale_dimension(box.width-attrs.left, scale)
                    element_height = scale_dimension(box.height-attrs.top, scale)

                    #print('V',element_width, element_height, scale)
                    #print('PO2', posterimage, posterimage.content, posterimage.object.filename)
                    img_width, img_height = self._resolve_image_geometry(
                        posterimage.object, element_width, element_height
                        )
                    #print('N', img_width, img_height)
                    slide.shapes.add_movie(
                        movie_file=value.content,
                        poster_frame_image=posterimage.object.filename,
                        top=element_top,
                        left=element_left,
                        width=img_width,
                        height=img_height,
                        )
                else:
                    # a pure warning on top?
                    shape = slide.shapes.add_textbox(
                        element_left, element_top, attrs.width, attrs.height
                    )
                    shape.text_frame.paragraphs[0].text = warning
  
            else:

                shape = slide.shapes.add_textbox(
                    element_left, element_top, attrs.width, attrs.height
                )
                copiedtags = deepcopy(element.tags)
                text_frame = shape.text_frame
                text_frame.paragraphs[0].text = element.thing.text_frame.text

                if copiedtags[0].child:
                    oldre = getReTag(copiedtags[0])
                    newtag = createTag(copiedtags[0].child)
                    #print('AAA', actions, newtag, copiedtags[0].child)
                    if copiedtags[0].child in actions and not warning:
                        replacestring = str(actions[copiedtags[0].child])
                    else:
                        replacestring = newtag.rawtag
                    replaceTextInRuns(
                        text_frame.paragraphs[0].runs, shape.text, oldre, replacestring
                    )
                    copiedtags[0] = newtag

                new_element = PptTextElement(shape, copiedtags)
                attrs.setFontAttrs(text_frame)

