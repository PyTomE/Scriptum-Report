#!/usr/bin/env python3
# coding: utf-8
#
# part of:
#   S C R I P T U M
#

from re import Pattern
from typing import Any, Callable, Mapping, MutableSequence, Optional, Sequence, Union

from ..tag import Tag

class Element(object):
    """Base Element class"""
    def __init__(self):
        
        self.parent = None
        self.tags = []
        self.type = None
        self.id = None
        self.isTemplate = False
        self.thing = None
        
    def __repr__(self) -> str:
        return f'element of type {self.type!r} : {self.id!r}'
        
    def hastag(self, tag: str) -> Union[bool,Tag]:
        """check if tag-string is in one of the tags of this element"""
        for t in self.tags:
            #print(' ---', tag,  t, t.puretag)
            if tag == t.puretag:
                return t
        else:
            return False
        
    def replaceTagInAll(self, tagname: str, replace: str) -> Any:
        """replace tags and burn them if found"""
        #print('   tag to replace',tagname, self.hastag(tagname), replace)
        found = False

        if (tag := self.hastag(tagname)) != False:
            #print('   inside replaceTagInAll:', tag, tagname)
            found = self.replaceTag(tag, replace)
            if found:
                tag.burn()
        if found is None:
            found = False
        return found

def replaceTextInRuns(
    runs: MutableSequence[Any],
    text: str,
    regex: Pattern[str],
    replace: str,
    ) -> Optional[Any]:
    """there is one issue with that routine:
    
    it looks that non-printable characters like newlines, at least in PPT, will fail this routine

    in that case the loop after print(SE...) will not start due to wrong indices?
    @TODO: further inevstigate
    """
    
    # now it is quite tricky to replace and search in the same loop
    runraster: list[int] = []
    s = 0
    # we may have several independent runs, which tells us the start indices in the full string
    for l in [ len(r.text) for r in runs ]:
        runraster += [s]
        s += l
    runraster += [s]
    
    # find inside full text the regex "tagre"
    # foundraster is a list of tuples telling the indices of matches start and end
    # old: foundraster = [ (f.start(),f.start()+len(f.group())) for f in tagre.finditer(text) ]
    foundraster = [ (f.start(),f.end()) for f in regex.finditer(text) ]
    #print('>>>',text,runraster, foundraster)
    
    # now we run the foundraster reversed since we replace which changes the indices of the matches at the right
    startrun: Optional[Any] = None
    for s,e in reversed(foundraster):
        #print('loop',s,e,text[s:e])
        eir = -1
        for ir,rr in enumerate(runraster):
            #print(s,e,rr,ir)
            if s>=rr: 
                sir = ir
            if e <= rr and eir == -1:
                eir = ir
        injected = False
        #print('SE', sir, eir)
        for ir in range(sir,eir):
            r = runs[ir]
            #print('work on run',ir,r.text,runraster[ir],s,runraster[ir+1],e)
            if runraster[ir] >= s and runraster[ir]+len(r.text) <= e:
                # fully clean some runs
                #print('case 1')
                r.text = ''
                startrun = r
            elif runraster[ir] <= s and runraster[ir+1] >= e:
                # fully inside
                #print('case 2')
                startrun = r
                r.text = r.text[:s-runraster[ir]]+replace+r.text[e-runraster[ir]:]
                injected = True
            elif runraster[ir] <= s and runraster[ir+1] > s:
                # middle of one run it starts
                #print('case 3', r.text, s-runraster[ir], r.text[:s-runraster[ir]])
                startrun = r
                r.text = r.text[:s-runraster[ir]]
            elif runraster[ir] <= e and runraster[ir+1] > e:
                # middle of one run it ends
                #print('case 4', r.text, e-runraster[ir], r.text[e-runraster[ir]:])
                r.text = r.text[e-runraster[ir]:]
            else:
                print('ERROR: uncaught situation, results might be unexpected')
                
            if not injected:
                r.text += replace
                injected = True
        #print()        
    #print('rt end   ',paragraph.text)
    return startrun

