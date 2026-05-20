#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# ///
"""Report drift between the pinned upstream SHA and support-docs HEAD.

Reads .upstream-reconciled-sha at repo root for the last-reconciled SHA,
diffs the support-docs submodule from there to HEAD, and groups changed
upstream files by which derivative skill file(s) draw from them.

Output is Markdown on stdout. Pipe into a file or hand to an agent to
drive the actual reconciliation edits.

Usage:
    uv run scripts/upstream_drift.py
    uv run scripts/upstream_drift.py --since <sha>
    uv run scripts/upstream_drift.py --no-diff
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUB = REPO / "support-docs"
SOURCES = REPO / "references" / "sources.toml"
PIN = REPO / ".upstream-reconciled-sha"
SOFT_DIR = REPO / "references" / "software"
UP_SOFT = "docs/Software/Available_Applications"


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=SUB, text=True)


def auto_software_map() -> dict[str, list[str]]:
    up_files = [l for l in git("ls-files", UP_SOFT).splitlines() if l.endswith(".md")]
    up_index = {Path(p).stem.lower().replace("_", ""): p for p in up_files}
    out: dict[str, list[str]] = {}
    for d in sorted(SOFT_DIR.glob("*.md")):
        if d.name == "index.md":
            continue
        if upstream := up_index.get(d.stem.replace("_", "")):
            out[str(d.relative_to(REPO))] = [upstream]
    return out


def load_mapping() -> dict[str, list[str]]:
    with SOURCES.open("rb") as f:
        explicit = dict(tomllib.load(f)["map"])
    mapping = auto_software_map()
    mapping.update(explicit)
    for d in sorted(SOFT_DIR.glob("*.md")):
        if d.name == "index.md":
            continue
        rel = str(d.relative_to(REPO))
        if rel not in mapping:
            print(f"warn: no upstream mapping for {rel}", file=sys.stderr)
    return mapping


def matches(path: str, pattern: str) -> bool:
    if pattern.endswith("/"):
        return path.startswith(pattern)
    return path == pattern


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--since", help="override the SHA from .upstream-reconciled-sha")
    ap.add_argument("--no-diff", action="store_true", help="omit inline diffs")
    args = ap.parse_args()

    if args.since:
        since = args.since
    elif PIN.exists():
        since = PIN.read_text().strip()
    else:
        print(
            f"error: {PIN.relative_to(REPO)} missing. Create it with the SHA you most "
            "recently reconciled against, or pass --since.",
            file=sys.stderr,
        )
        return 1

    head = git("rev-parse", "HEAD").strip()
    print("# Upstream drift report\n")
    print(f"Reconciled SHA: `{since[:12]}`  ")
    print(f"Submodule HEAD: `{head[:12]}`")

    if since == head:
        print("\nNo drift.")
        return 0

    raw = git("diff", "--name-status", f"{since}..HEAD", "--", "docs/")
    changes = [line.split("\t") for line in raw.splitlines() if line]
    mapping = load_mapping()

    grouped: dict[str, list[tuple[str, str]]] = {}
    unmapped: list[tuple[str, str]] = []
    for entry in changes:
        status, path = entry[0], entry[-1]
        hits = [d for d, prefixes in mapping.items() if any(matches(path, p) for p in prefixes)]
        if not hits:
            unmapped.append((status, path))
        for d in hits:
            grouped.setdefault(d, []).append((status, path))

    print(f"\nChanged upstream files: {len(changes)}  ")
    print(f"Derivatives needing review: {len(grouped)}  ")
    print(f"Unmapped upstream changes: {len(unmapped)}\n")

    for derivative, items in sorted(grouped.items()):
        print(f"## `{derivative}`\n")
        for status, path in items:
            print(f"- `{status}` `{path}`")
        print()
        if not args.no_diff:
            for _, path in items:
                diff = git("diff", f"{since}..HEAD", "--", path)
                if diff.strip():
                    print(f"<details><summary>diff for <code>{path}</code></summary>\n")
                    print("```diff")
                    print(diff.rstrip())
                    print("```\n")
                    print("</details>\n")

    if unmapped:
        print("## Unmapped upstream changes\n")
        print(
            "These upstream files changed but no derivative claims them. "
            "Extend `references/sources.toml` if any are relevant; otherwise ignore.\n"
        )
        for status, path in unmapped:
            print(f"- `{status}` `{path}`")

    return 0


if __name__ == "__main__":
    sys.exit(main())
