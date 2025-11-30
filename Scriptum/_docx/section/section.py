#!/usr/bin/env python3
# coding: utf-8
#
# part of:
#   S C R I P T U M 
#

from ..paragraphs import DocParagraphElement, delete_paragraph, delete_paragraph_if_empty
from ..tables import DocTableElement, delete_table
from ...tag.tag import Tag
from ..structure import StructuredElement
from docx.text.paragraph import Paragraph
from docx.table import Table
from itertools import chain
#from ..template import copy_paragraph_before, copy_table_before

class Section(StructuredElement):
    def __init__(self,section):
        """take a section object from python-pptx
        iterate and check it
        
        a section starts and ends with a paragraph and a tag.ns == section 
        for the very first and the very last of the contained paragraphs
        
        Thus, it might be a limitation, that no table can start or end a section (not tested)

        This means on the other side, that there can't be an "alinea" or "pilcrow" between
        </section:name> and the section break itself - which sometimes happens

        Maybe future option: ignore empty paragraphs from the last filled...
        But that allows for some misaligned documents ... probably...
        """

        self.section = section # native section...
        # start empty init later
        self.parent = '' # sections don't have a parent other than the document itself
        self.name = ''
        self.markedForDeletion = []
        self.structure = [] # will be reinitialized later

        _error = []
        _warning = []

        # FIRST OF ALL
        # find the very first paragraph and the last and check if that is a valid section
        # set its main tag and name
        # <section:foo>
        # </section:foo> -> anchor
        iterator = section.iter_inner_content()
        first = last = next(iterator, None)
        if not first:
            _error += ['Empty section found - check your document']
        else:
            # first one has to start as a paragraph!
            if type(first) != Paragraph:
                _error += ['Section is not starting with a Paragraph - check your document']
            else:
                obj = DocParagraphElement(first)
                if not obj.tags or obj.tags[0].ns != "section":
                    _error += ["Section doesn't start with a 'section'-tag - check your document",
                                   'Paragraph is:',
                                   f'  {obj.thing.text!r}',
                                   '  if empty: search for empty paragraphs between section tags']
                else:
                    self.tag = obj.tags[0]
                    self.name = self.tag.name
                    # now we don't need that tag anymore
                    self.markForDeletion(obj)
                    #obj.delete()

                # go to the last
                for last in iterator:
                    pass
                
                obj = DocParagraphElement(last)
                if not obj.tags or obj.tags[-1].ns != "section":
                    _error += ["Section doesn't end with a 'section'-tag - check your document"]
                else:
                    if self.tag and self.tag.name != obj.tags[-1].name:
                        _error += [
                            f"Section {self.tag.name!r} doesn't end with the same name - check your document"
                        ]
                    # now we don't need that tag anymore
                    #self.markForDeletion(obj)
                    #anchor = obj
                    #self.last = last

        if _error:
            self.error = _error
            self.warning = _warning
            return
        
        # NEXT STEP, rewind and
        # unfold it all -> make a long list of elements
        # for each tag get its element/paragraph or table it is connected to
        # keep elements without any tag in the order they do belong to
        # finally feed this long list to a StructuredElement as the main container
        # at this level we can "see" only pure paragraphs or tables

        # for a section we take the footers/headers as well and inject them into the section elements

        _elements = [ elem for elem in section.iter_inner_content() ]
        _lastelement = _elements[-1]
        if self.name != 'template': # ignore footer/header in template section
            _elements = _elements[:-1]+[ elem for elem in chain(
                            section.header.iter_inner_content(),
                            section.footer.iter_inner_content()) 
                            ] + [_lastelement]
        
        unfolded = []
        for elem in _elements:
            if type(elem) == Paragraph:
                obj = DocParagraphElement(elem)
                anchor = obj # keep last
            elif type(elem) == Table:
                obj = DocTableElement(elem)
            else:
                # note: image elements are part of a paragraph (even in table)
                # floating images are yet not supported (not implemented in python-docx v1.2)
                # thus, this error message will point to something unknown!
                _warning += [f"Unknown element type found {type(elem)!r}. Ignored!"]
                continue
            if not obj.tags:
                # simple and untagged element
                unfolded += [(None,obj)]
            else:
                ignore_rest = False
                for tag in obj.tags:
                    if tag.ns == 'ignore': # do ignore if...
                        if 'all' in tag.args and 'below' in tag.args:
                            # usually used only for the documentation section to avoid false warnings and errors
                            # however, we may use that in any section - what was never tested!
                            ignore_rest = True
                            break
                    if 'template' in tag.args and tag.tagtype == 'simple' and self.name != 'template':
                        _warning += [
                            f"Simple tag argument 'template' ({tag.puretag}) found outside the template section. Ignored!"
                        ]
                        continue
                    unfolded += [(tag,obj)]
                if ignore_rest: break
        
        # on each section there is only one structure!
        super().__init__(self.tag, [], None, unfolded, anchor)
        # keep errors and warning in the right order
        self.error = _error + self.error
        self.warning = _warning + self.warning

        # extract the whole structure
        self.explore()

        # extract all strcutures such taht we are able to find them fast
        self.addressbook = {}
        self.buildAddressbook()
        
    def delete(self):
        """remove the whole section
        
        we link this header to the previous

        since:

        > *a common cause is that deleting a section break merges the formatting from the section below it,* 
        > *not the one above. To fix this, you may need to link the header/footer to the previous section* 
        > *before deleting the break, or if the problem occurs at the end of the document, copy the header* 
        > *from the previous section to the new one and then delete the old section break.* 

        """
        for e in self.section.iter_inner_content():
            if type(e) == Paragraph:
                delete_paragraph(e)
            elif type(e) == Table:
                delete_table(e)
            else:
                print(f'how to delete this? {e}')

        if not self.section.header.is_linked_to_previous:
            print('INFO: Correcting header to be linked to previous to save previous header')
            self.section.header.is_linked_to_previous = True

        if not self.section.footer.is_linked_to_previous:
            print('INFO: Correcting footer to be linked to previous to save previous footer')
            self.section.footer.is_linked_to_previous = True

        # hp = None
        # for e in self.section.header.iter_inner_content():
        #     if type(e) == Paragraph:
        #         if not hp:
        #             hp = e
        #             e.text = ''
        #         else:
        #             delete_paragraph(e)
        #     elif type(e) == Table:
        #         delete_table(e)
        #     else:
        #         print(f'how to delete this? {e}')

        # fp = None
        # for e in self.section.footer.iter_inner_content():
        #     if type(e) == Paragraph:
        #         if not fp:
        #             fp = e
        #             e.text = ''
        #         else:
        #             delete_paragraph(e)
        #     elif type(e) == Table:
        #         delete_table(e)
        #     else:
        #         print(f'how to delete this? {e}')

        # # fix header (and footer) as described above
        # for e in keepheader.section.header.iter_inner_content():
        #     if type(e) == Paragraph:
        #         copy_paragraph_before(hp,deepcopy(e._p))
        #     elif type(e) == Table:
        #         copy_table_before(hp,deepcopy(e._tbl))
            
        # for e in keepheader.section.footer.iter_inner_content():
        #     if type(e) == Paragraph:
        #         copy_paragraph_before(fp,e._p)
        #     elif type(e) == Table:
        #         copy_table_before(fp,e._tbl)

        # finally remove the paragraph at which the section is anchored
        try:
            p = self.section._sectPr.getprevious()
            #print(type(p))
            #delete_paragraph(last)
            if p.getparent() is not None:
                p.getparent().remove(p)
                p._p = p._element = None
        except:
            pass

    def markForDeletion(self,elem):
        # overwrite the base class
        self.markedForDeletion += [elem]
    
    def buildAddressbook(self):
        """in order to store all structures in an addressable way, we setup a dictionary
        since the have to be unique..."""

        # the full organization of all structures:
        # base entry is this section
        # self.name = tag.name + self.type = tag.ns
        
        self.addressbook = {'.'.join(self.path): self}

        for e in self.iterOnStructures():
            self.addressbook['.'.join(e.path)] = e

