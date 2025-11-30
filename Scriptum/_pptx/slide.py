#!/usr/bin/env python3
# coding: utf-8
#
# part of:
#   S C R I P T U M 
#

from ..tag.tag import getTag
from . import PPTXTypes
from .base import replaceById
from .images import PptImageElement
from .paragraphs import PptTextElement
from .tables import PptTableElement
from .shapes import extract_placeholder_type

class Slide:
    
    def __init__(self, prs: PPTXTypes.Presentation, layout: PPTXTypes.CT_SlideLayout):
        """add and manage a slide from a given layout
        
        up to now new slides will be only appended
        once python-pptx can handle insertion this will be enhanced
        
        now connect placeholders within layout to those in slide itself
        both are NOT ALWAYS in same order but tags (what you replace) 
        are not 'visible' in slide-placeholders
        since idx (see docs of python-pptx) just now didn't work 
        there is a workaround to create an unique id
        by position and size of the placeholders... if not two are above each other...

        further information:
        a placeholder cannot be placed inside a group - thus groupshapes are impossible at this level
        
         * IDEA: test .shape_id and/or .name of shape - still not working
        
        """
        # setup
        self.layout = layout
        #print(type(layout))

        # add a new slide based on the layout
        self.slide = prs.slides.add_slide(layout)
        
        # be careful: these are the tags, but the placeholders from the layout not the final slide shapes
        self.tag_in_ph = {} # one tag might be in different/many placeholders
        self.ph = []   # series of placeholders (elements)
        #self.sph = {}
        
        # now we marry layoutplaceholders with slideplaceholders
        layout_ph_tags = []
        unusable = []
        
        # extract the placeholders we can use
        for ph in layout.placeholders:
            tags = getTag(ph.text)
            if not tags:
                unusable += [ph.text]
                continue

            phtype = extract_placeholder_type(ph)
            if phtype == 'unsupported':
                unusable += [f'{phtype!r} -> {ph.text!r}']
                continue

            # create a unique id by position -> assume we have not two or more placeholders by same size and position
            ph_id = (ph.left,ph.top,ph.width,ph.height)
            
            # for now keep here a list of tuples, maybe a dict wil do
            layout_ph_tags += [ (ph_id, phtype, tags) ]
            
        for ph in self.slide.placeholders:
            # extract again the unique id
            ph_id = (ph.left,ph.top,ph.width,ph.height)
            
            for i, (lph_id, phtype, tags) in enumerate(layout_ph_tags):
                if ph_id == lph_id:
                    if phtype == 'text':
                        _elems = [PptTextElement(ph, tags)]
                    elif phtype == 'table':
                        _elems = [PptTableElement(ph, tags)]
                    elif phtype == 'image':
                        _elems = [PptImageElement(ph, tags)]
                    elif phtype == 'multiple':
                        ## multiply it... but keep tags the same
                        #_elems = [PptTextElement(ph, tags), PptTableElement(ph, tags), PptImageElement(ph, tags)]
                        # take only a text element since we will not add tables or images to that template, we will overlay them!
                        _elems = [PptTextElement(ph, tags)]

                    self.ph += _elems
                    layout_ph_tags.pop(i)
                    for tag in tags:
                        self.tag_in_ph[tag.puretag] = self.tag_in_ph.get(tag.puretag,[])+_elems
                    break

        if unusable:
            print(f'WARNING: we found placeholders which cannot be used on layout {layout.name!r}')
            print('         Date/Time and some other special placeholders cannot be set by Scriptum yet.')
            print(f"         content: {' '.join(f'{u!r}' for u in unusable)}")

        if layout_ph_tags:
            print(f'WARNING: we lost some placeholders while creating the slide {layout.name!r}')
            print(
                f"         tags lost: {' '.join(tag.rawtag for phid, tags in layout_ph_tags for tag in tags)}"
            )

    def hide_placeholders(self):
        """set all empty placeholders to a single space
        which will "hide" them from view in PPT
        """
        
        for ph in self.ph:
            if hasattr(ph,'text') and ph.text == '':
                ph.text = ' '
    
    def multiply_placeholder(self, tagname: str, count: int, templates):
        """there are two placeholders with the same name
        find the first (from top and left) and the second
        and create count - 2 new placholders, rename the tags to
        tagname1, tagname2, ...
        
        not yet complete since clone/copy is not working"""

        shift = 100 # arbitrary

        c = len(templates)
        newElements = []
        if  c == 0:
            print(f'failed to find tags for numbering... {tagname!r}')
            
        elif c == 1:
            ph = templates[0]
            # copy element
            #somecopy(ph,ph.left,ph.top+shift,ph.width,ph.height)
        elif c >= 2:
            print(f'multiply_placeholder {len(templates)} {templates}')
            # sorted_ph = sorted(templates, 
            #                    key=lambda elem: elem.top+elem.left)[:2]
            # print(sorted_ph)
            # shiftx = sorted_ph[1].left-sorted_ph[0].left
            # shifty = sorted_ph[1].top-sorted_ph[0].top
            # # take the first
            # base = templates[0]

            # for i in range(2,count+2):
            #     newElem = base.copy(self,ph.left+i*shiftx,ph.top+i*shifty,ph.width,ph.height)
            #     newElem.text="<%s%d/>"%(tagname,i)
            #     newElements.append(newElem)
            #     #somecopy(sorted_ph[0],ph.left+i*shiftx,ph.top+i*shifty,ph.width,ph.height)
        return newElements

    def fitText(self,name=None,shape=None):
        """PPT behaves a bit strange on MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE and
        MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT. No matter what you use, it will first fit when
        you touch and change the shape interactively"""
        
        if name:
            shape = self._placeholders[replaceById(name)]
        tf = shape.text_frame
        tf.fit_text() # experimental
        #tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
        
