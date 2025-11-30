#!/usr/bin/env python3
"""Validate Scriptum RDF files."""

import argparse
#import importlib
#import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Callable, Iterable, Sequence


# either Scriptum is installed or we take the one that is hopefull relative to this file

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_PARENT = PROJECT_ROOT.parent
for candidate in (REPO_PARENT, PROJECT_ROOT):
    path_str = str(candidate)
    if path_str not in sys.path:
        sys.path.append(path_str)

try:
    import Scriptum
except:
    print('Cannot evaluate RDF file, package Scriptum not found!')
    SystemExit(1)

def _validate_rdf(paths: Iterable[Path], debug: bool) -> int:
    
    exit_code = 0
    rdf_file = None
    for path in paths:
        if not path.exists():
            print(f"{path}: file not found")
            exit_code = max(exit_code, 2)
            continue

        buffer: io.StringIO | None = None
        try:
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                rdf_file = Scriptum.ReportDataFile(str(path), debug=debug)
        except Exception as exc:  # pragma: no cover - runtime guard
            print(f"{path}: failed to parse RDF file: {exc}")
            exit_code = max(exit_code, 2)
            continue

        if debug and buffer is not None:
            captured = buffer.getvalue()
            if captured:
                print(captured, end="")

        errors = getattr(rdf_file, "errors", [])
        visited = getattr(rdf_file, "_visited", set([]))
        
        if errors:
            print(f"{path}: invalid Scriptum RDF file")
            print('files inspected:')
            for entry in visited:
                print(f'    - {entry}')
            print('errors detected:')
            for entry in errors:
                print(f"    - {entry}")
            exit_code = max(exit_code, 1)
        else:
            print(f"{path}: valid Scriptum RDF definition")
            print('files inspected:')
            for entry in visited:
                print(f'    - {entry}')

    return exit_code


def _parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Scriptum RDF files.",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="RDF file(s) to validate.",
    )
    #parser.add_argument(
    #    "--debug",
    #    action="store_true",
    #    help="Show verbose output from Scriptum internals.",
    #)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_arguments(argv if argv is not None else sys.argv[1:])
    return _validate_rdf(args.paths, True)#args.debug)


if __name__ == "__main__":
    raise SystemExit(main())
