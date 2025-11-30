"""Paragraph-related element implementations for PowerPoint rendering."""

from typing import List

from ...element import ParagraphElement
from ...tag import Tag, getTag
from ..base import PptElement


class PptTextElement(PptElement):
    """Text elements are the generic shape to hold paragraphs."""

    def __init__(self, elem, tags):
        super().__init__(elem)
        self.tags = tags
        self.paragraphs: List[PptParagraphElement] = []
        self.type = "text"

        if elem.text_frame.paragraphs:
            for paragraph in elem.text_frame.paragraphs:
                paragraph_tags = getTag(paragraph.text)
                self.paragraphs.append(PptParagraphElement(paragraph, paragraph_tags))

    def replaceTag(self, tag: Tag, replace: str):
        if self.isplaceholder:
            self.thing.text = replace
            return True

        for paragraph in self.paragraphs:
            if paragraph.replaceTag(tag, replace):
                placeholder_tag = self.hastag(tag.puretag)
                if placeholder_tag:
                    placeholder_tag.burn()
                return True
        return False


class PptParagraphElement(ParagraphElement):
    """Paragraphs inside a text element."""

    def __init__(self, elem, tags):
        super().__init__()
        self.tags = tags
        self.thing = elem
        self.isplaceholder = False
        self.type = "paragraph"
