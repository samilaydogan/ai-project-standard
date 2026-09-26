"""Bounded links, placeholders and JSON syntax; no vocabulary policy."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

EXCLUDED = {
    "vendor",
    "node_modules",
    "build",
    "dist",
    "data",
    "postgres-data",
    "backups",
    "__pycache__",
}
LINK = re.compile(
    r"""(?<!!)\[[^\]\n]+\]\(\s*(?:<([^>\n]+)>|([^\s()\n]+))(?:\s+["'][^"'\n]*["'])?\s*\)"""
)
PLACEHOLDER = re.compile(r"\{\{[A-Za-z0-9_]+\}\}")


def prose(text: str) -> str:
    lines = []
    fence = None
    for line in text.splitlines(keepends=True):
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1]:
                fence = None
            lines.append("\n")
        elif fence is None:
            lines.append(line)
        else:
            lines.append("\n")
    return re.sub(r"(`+)[^`]*?\1", "", "".join(lines))


def selected(root: Path, files: list[str] | None) -> list[Path]:
    if files is not None:
        paths = []
        for name in files:
            relative = Path(name)
            path = root / relative
            if (
                relative.is_absolute()
                or ".." in relative.parts
                or path.is_symlink()
                or not path.resolve().is_relative_to(root.resolve())
                or not path.is_file()
                or path.suffix not in {".md", ".json"}
            ):
                raise ValueError(f"{name}: TEST-APPLICABILITY unsupported/missing scan member")
            paths.append(path)
        return sorted(set(paths))
    paths = []
    for path in root.rglob("*"):
        parts = path.relative_to(root).parts
        if any(part.startswith(".") or part in EXCLUDED for part in parts):
            continue
        if path.suffix in {".md", ".json"} and path.is_file() and not path.is_symlink():
            paths.append(path)
    return sorted(paths)


def check(root: Path, files: list[str] | None = None) -> tuple[list[str], dict]:
    root = root.resolve()
    errors = []
    paths = selected(root, files)
    md_count = json_count = 0
    for path in paths:
        name = path.relative_to(root).as_posix()
        raw = path.read_text()
        if path.suffix == ".md":
            md_count += 1
            text = prose(raw)
            for match in LINK.finditer(text):
                target = match.group(1) or match.group(2)
                if urlsplit(target).scheme or target.startswith("#"):
                    continue
                filepart = unquote(target.split("#", 1)[0])
                if filepart and not (path.parent / filepart).exists():
                    errors.append(
                        f"{name}: TEST-APPLICABILITY broken supported local link {target}"
                    )
        else:
            json_count += 1
            text = raw
            try:
                json.loads(raw)
            except ValueError:
                errors.append(f"{name}: ADP-STRUCTURE invalid JSON")
        if ".template." not in path.name:
            for match in PLACEHOLDER.finditer(text):
                errors.append(f"{name}: ADP-STRUCTURE unresolved placeholder {match.group()}")
    return errors, {"markdown": md_count, "json": json_count}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path.cwd())
    parser.add_argument("--files", nargs="+", help="Explicit affected Markdown/JSON paths")
    args = parser.parse_args()
    try:
        errors, scope = check(args.root, args.files)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"FAIL: bounded docs scan: {exc}")
        return 1
    if errors:
        print("\n".join(errors))
        return 1
    print(
        f"BOUNDED DOCS QUALITY PASS: {scope['markdown']} Markdown / {scope['json']} JSON; "
        "supported inline local links/non-template placeholders/JSON syntax"
    )
    print(
        "NOT ASSESSED: vocabulary/project neutrality, external URLs, anchors, images, "
        "reference links, facts or policy acceptance"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
