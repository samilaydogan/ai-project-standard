"""Bounded docs quality: supported inline links/placeholders; optional distribution lexical scan."""

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
# vocabulary-pattern: begin
VOCABULARY = re.compile(
    r"\b(?:OperationHub|Tenant|Company|CompanyMembership|invoice|invoices|orders|cargo|"
    r"Google|AuthHub|eLogo|Nilvera|Tabler|Paraşüt)\b|\b[A-Z][0-9]?/\d{2,3}\b",
    re.IGNORECASE,
)
# vocabulary-pattern: end


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
    release_path = root / "standard-release.json"
    vocabulary_count = None
    if release_path.is_file():
        release = json.loads(release_path.read_text())
        vocabulary_count = 0
        for name in sorted(release["files"]):
            relative = Path(name)
            path = root / relative
            if (
                relative.is_absolute()
                or ".." in relative.parts
                or path.is_symlink()
                or not path.resolve().is_relative_to(root)
            ):
                errors.append(f"{name}: ADP-INTEGRITY unsafe lexical scan member")
                continue
            if path.suffix not in {".md", ".json", ".py"}:
                continue
            vocabulary_count += 1
            text = path.read_text()
            if name == "scripts/check_docs.py":
                text = re.sub(
                    r"# vocabulary-pattern: begin.*?# vocabulary-pattern: end",
                    "",
                    text,
                    flags=re.DOTALL,
                )
            for match in VOCABULARY.finditer(text):
                errors.append(f"{name}: ADP-INTEGRITY source-project vocabulary {match.group()}")
    return errors, {"markdown": md_count, "json": json_count, "vocabulary": vocabulary_count}


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
    vocabulary = (
        f"{scope['vocabulary']} distributed text files scanned"
        if scope["vocabulary"] is not None
        else "NOT RUN (no standard release manifest)"
    )
    print(
        f"BOUNDED DOCS QUALITY PASS: {scope['markdown']} Markdown / {scope['json']} JSON; "
        f"supported inline local links/non-template placeholders; vocabulary {vocabulary}"
    )
    print(
        "NOT ASSESSED: external URLs, anchors, images, reference links, facts or policy acceptance"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
