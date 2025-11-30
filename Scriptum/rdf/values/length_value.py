"""Utilities for dealing with length values."""

import types

class LengthValue:
    """Extract lengths."""

    def __init__(self, value: str):
        _value = value.lower()
        if 'inch' in _value:
            self.unit = 'in'
            _value = _value[:-4]
        else:
            self.unit = _value[-2:]
            _value = _value[:-2]

        try:
            self.value = float(_value)
        except Exception:
            self.value = f'cannot evaluate length: {value}'

    @property
    def content(self):
        return self.value

    def __repr__(self) -> str:
        return f"{self.value} - unit: {self.unit}"

    def __str__(self) -> str:
        return str(self.value)

ZeroLengthValue = types.ModuleType('ZeroLength')
ZeroLengthValue.object = LengthValue('0cm')
ZeroLengthValue.type = 'length'