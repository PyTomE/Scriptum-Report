"""Helpers for parsing date values."""

import re
from datetime import datetime

try:
    from dateutil import parser as date_parser
except ModuleNotFoundError:  # pragma: no cover - fallback for environments without python-dateutil
    class _SimpleDateParser:
        """Lightweight fallback parser approximating :mod:`dateutil.parser`."""

        _FORMATS = [
            '%m/%d/%y %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d',
            '%m/%d/%y',
            '%m/%d/%Y',
            '%a %b %d %H:%M:%S %Y',
            '%H:%M:%S',
            '%H:%M',
        ]

        @staticmethod
        def parse(value: str) -> datetime:
            trimmed = value.strip()
            if not trimmed:
                raise ValueError('Empty date string')

            iso_candidate = trimmed.replace('Z', '+00:00')
            try:
                return datetime.fromisoformat(iso_candidate)
            except ValueError:
                pass

            for fmt in _SimpleDateParser._FORMATS:
                try:
                    return datetime.strptime(trimmed, fmt)
                except ValueError:
                    continue

            raise ValueError(f"Unable to parse date string: {value!r}")

    date_parser = _SimpleDateParser()

from ..common import removeQuotes


class DateValue:
    """DateValues are either
    date:now                      -> date:now
    date:now:format               -> date:now:'%d. %b %Y -- %H:%M:%S'
    date:today                    -> date:today
    date:today:format             -> date:today:'%d. %b %Y'
    date:integer-timestamp        -> date:1231231230
    date:integer-timestamp:format -> date:1231231230:'%d. %b %Y -- %H:%M:%S'
    date:quoted-timestring        -> date:'12/15/22 14:24:59'
    date:quoted-timestring:format -> date:'12/15/22 14:24:59':'%m.%d.%y %H:%M:%S'
    """
    def __init__(self, v: str, settings={}):
        
        if v.startswith('now'):
            v = v.replace('now', '', 1)
            if v.startswith(':') and len(v) > 1:
                self.format = removeQuotes(v[1:])
            else:
                self.format = settings.datetimeformat
            dt = datetime.now()
            value = dt.strftime(self.format)
        elif v.startswith('today'):
            v = v.replace('today', '', 1)
            if v.startswith(':') and len(v) > 1:
                self.format = removeQuotes(v[1:])
            else:
                self.format = settings.dateformat
            dt = datetime.today()
            value = dt.strftime(self.format)
        else:
            tokens = []
            current = []
            quote_char = None

            for ch in v:
                if ch in {"'", '"'}:
                    if quote_char is None:
                        quote_char = ch
                    elif quote_char == ch:
                        quote_char = None
                    current.append(ch)
                elif ch == ':' and quote_char is None:
                    tokens.append(''.join(current))
                    current = []
                else:
                    current.append(ch)

            tokens.append(''.join(current))

            dt = None
            explicit_format = None

            numeric_re = re.compile(r'^[-+]?\d+(?:\.\d+)?$')

            for i in range(1, len(tokens) + 1):
                candidate_value = ':'.join(tokens[:i]).strip()
                candidate_format = ':'.join(tokens[i:]).strip() if i < len(tokens) else ''

                value_text = removeQuotes(candidate_value)
                format_text = removeQuotes(candidate_format) if candidate_format else ''

                if not value_text:
                    continue

                parsed_dt = None

                if numeric_re.match(value_text):
                    try:
                        ts_value = float(value_text)
                        if '.' not in value_text and len(value_text.lstrip('+-')) >= 13:
                            ts_value /= 1000.0
                        parsed_dt = datetime.fromtimestamp(ts_value)
                    except Exception:
                        parsed_dt = None

                if parsed_dt is None:
                    try:
                        parsed_dt = date_parser.parse(value_text)
                    except Exception:
                        continue

                dt = parsed_dt
                explicit_format = format_text or None
                break

            if dt is None:
                dt = datetime.fromtimestamp(0)

            if explicit_format:
                self.format = explicit_format
            else:
                self.format = settings.datetimeformat

            try:
                value = dt.strftime(self.format)
            except Exception:
                value = dt.strftime(settings.dateformat)

        self.value = value
        self.dt = dt

    @property
    def content(self):
        return str(self)

    def __repr__(self) -> str:
        return f"'{self.value}' - use format '{self.format}'"

    def __str__(self) -> str:
        return self.value
