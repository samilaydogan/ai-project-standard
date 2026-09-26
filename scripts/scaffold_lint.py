"""Bounded Python syntax and trailing-whitespace check; no imports or cache writes."""

import ast
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
errors = []
for pattern in ("scripts/*.py", "tests/*.py"):
    for path in sorted(root.glob(pattern)):
        try:
            ast.parse(path.read_text(), filename=str(path))
        except SyntaxError as exc:
            errors.append(str(exc))
        for line, text in enumerate(path.read_text().splitlines(), 1):
            if text.rstrip() != text:
                errors.append(f"{path.relative_to(root)}:{line}: trailing whitespace")
print(
    "\n".join(errors)
    if errors
    else ("BOUNDED LINT PASS: scripts/tests Python syntax and trailing whitespace; "
          "no type/style proof")
)
sys.exit(bool(errors))
