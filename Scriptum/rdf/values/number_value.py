"""Helpers for numbering values."""

import types

class IntegerValue:
    def __init__(self, value: int):
        self.value = value
        
    @property
    def content(self):
        return str(self)

    def __repr__(self) -> str:
        return f"{self.value!r}"

    def __str__(self) -> str:
        return str(self.value)

class FloatValue:
    def __init__(self, value: float, settings=None):
        if settings is None:
            settings = {}
        self.value = value
        self.floatformat = getattr(settings, 'floatformat', '7.4f')

    @property
    def content(self):
        return str(self)

    def __repr__(self) -> str:
        return f"'{self.value}' - use format '{self.floatformat}'"

    def __str__(self) -> str:
        fformat = (f"{{:{self.floatformat}}}").format
        return fformat(self.value)

class NumberValue:
    """Class to define different section number formats."""

    def __init__(self, value: str):
        """Extract a numbering type list out of the content."""

        err = False
        try:
            all_parts = value.split(':')
        except Exception:
            self.str = f'- failed to read {value!r}'
            values = []
            err = True
        else:
            if len(all_parts) == 2:
                k, f = all_parts
                s = '1'
            elif len(all_parts) == 3:
                k, f, s = all_parts
            else:
                self.str = f'- failed to interprete {value!r}'
                values = []
                err = True

        if not err:
            try:
                if k != 'F':
                    s = int(s)
            except Exception:
                self.str = f'- failed to understand {value!r}'
                values = []
                err = True

        if not err:
            values = []
            if k == 'F':
                values = [f % v for v in s.split(';')]
                s = 1
            else:
                for i in range(100):
                    if k == '1':
                        values += [f % (i + 1)]
                    elif k == 'a':
                        values += [f % chr(i + 97)]
                        if i >= 26:
                            break
                    elif k == 'A':
                        values += [f % chr(i + 65)]
                        if i >= 26:
                            break
                    elif k == 'i':
                        values += [(f % self._int_to_roman(i + 1)).lower()]
                        if i >= 39:
                            break
                    elif k == 'I':
                        values += [f % self._int_to_roman(i + 1)]
                        if i >= 39:
                            break
                    else:
                        self.str = f'- unknown number format in {value!r}'
                        values = []
                        err = True
                        break

            values = values[s - 1:]

        if not err:
            self.str = '[ ' + str(values[:3])[1:-1] + ', ... ]'

        self.numbers = iter(values)

    def __next__(self):
        return next(self.numbers)

    @staticmethod
    def _int_to_roman(input: int) -> str:
        """Convert an integer to a Roman numeral (up to 39)."""

        ints = (10, 9, 5, 4, 1)
        nums = ('X', 'IX', 'V', 'IV', 'I')
        result = []
        for i in range(len(ints)):
            count = int(input / ints[i])
            result.append(nums[i] * count)
            input -= ints[i] * count
        return ''.join(result)

    def __repr__(self) -> str:
        return self.str

    @property
    def content(self):
        return next(self)

ZeroValue = types.ModuleType('ZeroFloat')
ZeroValue.object = FloatValue(0.0)
ZeroValue.type = 'float'
