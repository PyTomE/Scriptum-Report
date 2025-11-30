from typing import Union

from pptx.util import Pt, Cm, Mm, Inches
from typing import Any, Callable, Mapping, Optional, Union

units = {
    'cm': Cm,
    'mm': Mm,
    'pt': Pt,
    'in': Inches,
    'inch': Inches,
}

def InCm(value: Union[int, float]) -> float:
    return float(value)/Cm(1)

def getLengthFromString(
    length: str,
    units: Mapping[str, Callable[[float], Any]],
) -> Optional[Any]:
    """convert into pptx/docx units"""
    if length.endswith('px'):
        unit = units['pt']
        length = length[:-2]
    elif length.endswith('mm'):
        unit = units['mm']
        length = length[:-2]
    elif length.endswith('cm'):
        unit = units['cm']
        length = length[:-2]
    elif length.endswith('in'):
        unit = units['inch']
        length = length[:-2]
    else:
        unit = units['pt']
    try:
        numeric = eval(length)
        return unit(numeric)
    except Exception:
        return None

