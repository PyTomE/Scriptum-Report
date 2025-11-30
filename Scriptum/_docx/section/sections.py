#!/usr/bin/env python3
# coding: utf-8
#
# part of:
#   S C R I P T U M 
#

from .section import Section

class Sections:
    """contains only sections as structured elements"""
    def __init__(self, sections):
        """will create the root elements of all and parse them
        sections are always the container everything is in"""
        
        self._sections = [ Section(s) for s in sections ]
        self._fillTemplates()

    def __iter__(self):
        """iterate content"""
        yield from iter(self._sections) # which is a list

    def byName(self,name):
        """find a section by name"""
        name = name.replace('section:','')
        for s in self:
            if s.name == name:
                return s
    
    def findGlobal(self, what: str) -> list:
        """find in all sections
        * what is a string"""

        result = []
        # this is brute force we simply walk over everything but template section
        for sec in self:
            if sec.name == 'template': continue
            result += sec.findGlobal(what)
        
        return result

    def _fillTemplates(self):
        """generate all templates"""
        result = []
        for sec in self._sections:
            result += sec.getTemplates()

        self.templates = result
    
    def findTemplate(self, name):
        """find one template by path or string <- name"""
        if type(name) == str:
            # we expect this template inside the section:template
            name = ['section:template', name]
        for t,e in self.templates:
            if name == e.path:
                return e
        print(f'WARNING: No such template in document: {name}')
    
    def delete(self, sectionname):
        s = self.byName(sectionname)
        s.delete()

