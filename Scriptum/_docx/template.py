#!/usr/bin/env python3
# coding: utf-8
#
# part of:
#   S C R I P T U M 

#
from copy import deepcopy
from docx.text.paragraph import Paragraph
from docx.enum.text import WD_BREAK
from docx.table import Table

class Template:
    """a template is one of
    - Paragraph - quite simple from simple tagged entries and only from section:template
    - StructuredElement - consist of paragraphs and tables enclosed in open/close tags

    templates can be added to marker:content or to the end of a previous template (close-tag)
    """

    def __init__(self, ttype, element):

        if ttype == 'struct':
            self.type = 'struct'
            self.path = element.path
            _elements = []
            for p,t,e in element: # we need only the elements from now on, tags are derived again below
                if e not in _elements: _elements.append(e)
            # and we need them only once
            #self.elements = [ determineElement(e) for e in _elements ]   
            self.elements = _elements  

        else:
            self.type = 'simple'
            self.path = ['section:template',ttype.puretag] # simple tags are always in the template section, even if not ?
            self.elements = [element]
            
    def inspect(self):
        """visualize the content of that element"""
        print(f'TEMPLATE (start): {self.type} path={self.path}')
        for elem in self.elements:
            print(f'  element: {elem}')
        print(f'TEMPLATE (end): {self.path}')

def copy_table_before(anchor_paragraph, source_table):
    """Return copy of `source_table`, inserted directly before `anchor_paragraph`."""
    #new_tbl = deepcopy(source_table._tbl)
    new_tbl = deepcopy(source_table)
    anchor_paragraph._p.addprevious(new_tbl)
    return Table(new_tbl, anchor_paragraph._parent)

def copy_paragraph_before(anchor_paragraph, source_paragraph):
    """Return copy of `source_paragraph`, inserted directly before `anchor_paragraph`."""
    #new_p = deepcopy(source_paragraph._p)
    new_p = deepcopy(source_paragraph)
    anchor_paragraph._p.addprevious(new_p)
    return Paragraph(new_p, anchor_paragraph._parent)

def add_page_break_before(anchor_paragraph):
    """Return newly |Paragraph| object containing only a page break."""
    paragraph = anchor_paragraph.insert_paragraph_before()
    paragraph.add_run().add_break(WD_BREAK.PAGE)
    return paragraph

