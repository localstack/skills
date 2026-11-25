#!/usr/bin/env python3
"""Cross-file consistency checks for the skills repo. Stdlib only.

skills-ref validates each SKILL.md on its own. This script checks what
only shows up across files:

  - plugin.json, .claude-plugin/plugin.json, and the marketplace entry
    agree on name, version, description, and shared metadata
  - the marketplace entry points at the repository root
  - every "`<skill>` skill" reference names an existing skill
  - every #anchor link resolves to a heading in the same file
  - every relative file link resolves to a path in the repo
  - the README skills table lists exactly the directories under skills/

Exit code 0 when everything passes, 1 otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
ROOT_MANIFEST = ROOT / "plugin.json"
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

# Fields every manifest that carries them must agree on.
SHARED_FIELDS = ("name", "version", "description", "author", "license", "homepage", "repository", "keywords")
# The marketplace entry carries only a subset, and all of these are required.
MARKETPLACE_FIELDS = ("name", "version", "description", "author")

SKILL_REF_RE = re.compile(r"`((?:localstack|lstk)[a-z0-9-]*)` skill")
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
README_SKILL_ROW_RE = re.compile(r"^\|\s*\[[^\]]+\]\(skills/([^/)]+)/?\)")

errors: list[str] = []


def fail(path: Path, msg: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {msg}")


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        fail(path, f"cannot read JSON: {exc}")
        return None


def check_manifests() -> None:
    root = load_json(ROOT_MANIFEST)
    claude = load_json(CLAUDE_MANIFEST)
    market = load_json(MARKETPLACE)
    if root is None:
        return

    if claude is not None:
        for key in SHARED_FIELDS:
            if key in root and claude.get(key) != root[key]:
                fail(CLAUDE_MANIFEST, f"{key} {claude.get(key)!r} differs from plugin.json {root[key]!r}")

    if market is None:
        return
    entries = [p for p in market.get("plugins", []) if p.get("name") == root.get("name")]
    if len(entries) != 1:
        fail(MARKETPLACE, f"expected one plugin entry named {root.get('name')!r}, found {len(entries)}")
        return
    entry = entries[0]
    if entry.get("source") != "./":
        fail(MARKETPLACE, f'plugin source is {entry.get("source")!r}; expected "./"')
    for key in MARKETPLACE_FIELDS:
        if entry.get(key) != root.get(key):
            fail(MARKETPLACE, f"plugin {key} {entry.get(key)!r} differs from plugin.json {root.get(key)!r}")


def strip_code_blocks(text: str) -> list[str]:
    """Blank out fenced code so headings and links inside it are ignored."""
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else line)
    return out


def github_slug(heading: str) -> str:
    """Approximate GitHub's heading anchor algorithm."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors_of(lines: list[str]) -> set[str]:
    seen: dict[str, int] = {}
    anchors = set()
    for line in lines:
        m = HEADING_RE.match(line)
        if not m:
            continue
        slug = github_slug(m.group(2))
        n = seen.get(slug, 0)
        anchors.add(slug if n == 0 else f"{slug}-{n}")
        seen[slug] = n + 1
    return anchors


def check_markdown(path: Path, skill_names: set[str]) -> None:
    lines = strip_code_blocks(path.read_text())
    anchors = anchors_of(lines)
    for lineno, line in enumerate(lines, 1):
        for ref in SKILL_REF_RE.findall(line):
            if ref not in skill_names:
                fail(path, f"line {lineno}: references unknown skill `{ref}`")
        for target in LINK_RE.findall(line):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target):  # http:, https:, mailto:
                continue
            file_part, _, anchor = target.partition("#")
            if file_part:
                if not (path.parent / file_part).exists():
                    fail(path, f"line {lineno}: link to missing path {target!r}")
            elif anchor and anchor not in anchors:
                fail(path, f"line {lineno}: anchor #{anchor} matches no heading")


def check_readme_table(skill_names: set[str]) -> None:
    readme = ROOT / "README.md"
    listed = {m.group(1) for line in readme.read_text().splitlines() if (m := README_SKILL_ROW_RE.match(line))}
    for missing in sorted(skill_names - listed):
        fail(readme, f"skills table does not list skills/{missing}/")
    for extra in sorted(listed - skill_names):
        fail(readme, f"skills table lists skills/{extra}/, which has no SKILL.md")


def main() -> int:
    check_manifests()
    skill_names = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}
    for md in sorted([ROOT / "README.md", *SKILLS_DIR.glob("*/*.md")]):
        check_markdown(md, skill_names)
    check_readme_table(skill_names)
    if errors:
        print(f"{len(errors)} consistency problem(s):", *errors, sep="\n  ")
        return 1
    print(f"Consistency OK: 3 manifests, {len(skill_names)} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
