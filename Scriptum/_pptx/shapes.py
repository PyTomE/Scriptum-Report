#!/usr/bin/env python3
# coding: utf-8
#
# part of:
#   S C R I P T U M 
#

#
from ..tag.tag import getTag
from . import known_placeholder_types, known_shape_types
from .images import PptImageElement
from .paragraphs import PptTextElement
from .tables import PptTableElement

def getShapes(source, placeholder:bool = False) -> list:
    """extract shapes from the source, 
    
    source is a slide, a layout or a groupshape
    for templates it could be just the source for one shape
    placeholder = False for all shapes but placeholders e.g. templates in config-slides
                = True for only placeholders on normal layouts

    on a slide we will find only placeholders or added shapes (none from the layout)
    current pptx limitations:
    - we cannot extract picture shapes unless they are part of a group
    
    """
    shapes = []

    if placeholder:
        _source = source.placeholders
        _shtype = lambda x: known_placeholder_types.get(x.placeholder_format.type,'unsupported')
    elif hasattr(source, 'shapes'):
        _source = source.shapes
        _shtype = lambda x: known_shape_types.get(x.shape_type,'unsupported')
    else:
        # single shape, seems to be a template
        _source = [source]
        _shtype = lambda x: known_shape_types.get(x.shape_type,'unsupported')
        
    for shape in _source:
        shtype = _shtype(shape)
        #print(shape,shtype)
        if shtype == 'unsupported':
            continue # ignore

        if shtype == 'text':
            #print(shape.text)
            tags = getTag(shape.text)
            shapes += [PptTextElement(shape, tags)]
        elif shtype == 'table':
            tags = getTag(shape.table.cell(0,0).text)
            shapes += [PptTableElement(shape, tags)]
        elif shtype in ['image','frame']:
            tags = getTag(shape.text)
            shapes += [PptImageElement(shape, tags)]
        elif shtype == 'group':
            shapes += getShapes(shape)# group shapes - never touched within placeholders
        else:
            pass

    return shapes
                
def extract_placeholder_type(placeholder):
    """raw extract of the placeholder type"""

    t = placeholder.placeholder_format.type
    return known_placeholder_types.get(t,'unknown')

class Unused_Shape:
    """all shapes other than GroupShapes"""
    def __init__(self,shape):
        self.shape = shape
        if hasattr(shape,'text'):
            self.tags = getTag(shape.text)
        else:
            self.tags = []

