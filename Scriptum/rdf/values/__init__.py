"""Value subpackage exposing common value classes.

Values are the singletons to get info from rdf (config) and put it to elements (result = pptx/docx...)
"""

from .base import Value
from .date_value import DateValue
from .file_value import FileValue
from .length_value import LengthValue
from .number_value import NumberValue, FloatValue, IntegerValue
from .image_value import ImageValue, AnimationValue
from .namevalues_value import NameValue
from .text_value import TextValue, StringValue
from .table_value import TableValue, Table
from .color_value import ColorValue

__all__ = [
    'Value',
    'DateValue',
    'FileValue',
    'FloatValue',
    'IntegerValue',
    'LengthValue',
    'NumberValue',
    'TableValue',
    'Table',
    'TextValue',
    'StringValue',
    'ImageValue',
    'AnimationValue',
    'NameValue',
    'ColorValue',
    ]
