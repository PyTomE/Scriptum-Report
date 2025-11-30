"""Value helpers for file-based inputs."""

import os

class FileValue:
    """Generic file-type objects."""

    def __init__(self, filename: str, exists: bool = False):
        self.filename = filename
        self.subtype = 'unclear'
        self.exists = exists

    def __repr__(self) -> str:
        return f"{self.filename!r} exists: {self.exists} ({self.subtype})"

    def __str__(self) -> str:
        return str(self.filename)

    @property
    def content(self):
        return f"content/type of file {self.filename!r} is unclear"