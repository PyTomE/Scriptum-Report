"""Shared helpers for rdf module."""

import os
from typing import Tuple

_test_debug = False


def set_test_debug(value: bool) -> None:
    """Set the test debug flag used to silence noisy output in tests."""
    global _test_debug
    _test_debug = value


def is_test_debug() -> bool:
    """Return whether test debug mode is enabled."""
    return _test_debug


def removeQuotes(v: str) -> str:
    """Extract a value even if it is enclosed by quotes."""
    if v and ((v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"'))):
        v = v[1:-1]
    return v


def getCorrectFile(name: str, relative: bool = False, datadir: str = '.') -> Tuple[str, bool]:
    """Find the correct file, optionally considering relative paths."""
    exists = False
    if name == os.path.abspath(name):
        name = os.path.normpath(os.path.join(datadir, name))
        if os.path.exists(name):
            exists = True
    else:
        if relative and os.path.exists(name):
            exists = True
        else:
            name = os.path.normpath(os.path.join(datadir, name))
            exists = os.path.exists(name)
    return name, exists


