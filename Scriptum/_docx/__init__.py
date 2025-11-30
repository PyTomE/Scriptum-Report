# part of:
#   S C R I P T U M 

from docx.oxml.ns import qn
wordtags = { 'w:instrText': qn('w:instrText'),
             'w:drawing': qn('w:drawing'),
             'm:oMath': qn('m:oMath'),
             'w:sdtContent': qn('w:sdtContent') }

# what is the name and level
sectionnames = {
    0: 'section',
    1: 'subsection',
    2: 'subsubsection',
    3: 'sub3section',
    4: 'sub4section',
    5: 'sub5section',
}

sectionorder = [ sectionnames[i] for i in range(max(sectionnames.keys()))]

docx_sections = { 'order': sectionorder,
                  'names': sectionnames,
                  'mandatory': True
                  }


__all__ = ["wordtags", 'docx_sections']


