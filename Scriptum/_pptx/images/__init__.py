"""Image feature package."""

from typing import TYPE_CHECKING

from .element import PptImageElement, delete_shape, getSizeFrom
from .template import ImageTemplate, AnimationTemplate

__all__ = ["PptImageElement", "ImageTemplate", "AnimationTemplate", "delete_shape", "getSizeFrom"]

