#!/usr/bin/env python3
#
# part of:
#   S C R I P T U M 
#

from ..element import Element

class DocElement(Element):
    """all types of elements with some metadata for WORD documents
    unique ID - str
    highlevel element - python-docx
    lowlevel xml element - python-docx, lxml
    objecttype:
        paragraph, 
        table, 
        section (which is a paragraph itself),
        other - table of contents, figures etc, which will stay as they are
    unsupported are e.g. table of tables 
    """
    def __init__(self, elem):
        # init an element (generic)
        super().__init__()
        # DOCX elements have no known id, thus create one
        self.id = str(elem)
        # required later in paragraphs
        #self._elem = elem
        # it is yet not known, maybe later
        self.type = 'other'
                        
