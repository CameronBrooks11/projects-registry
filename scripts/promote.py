#!/usr/bin/env python3
"""
Promote one or more pending project stubs to data/projects/.

Usage:
    python scripts/promote.py <id> [<id> ...]
    python scripts/promote.py --audit          # report pending file quality

The script validates each file against the schema before moving it.
Files that fail validation are left in pending/ and reported.
"""

from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PENDING_DIR = ROOT / "data" / "pending"
PROJECTS_DIR = ROOT / "data" / "projects"
SCHEMA_PATH = ROOT / "schema" / "project.schema.json"
GEN = ROOT / "scripts" / "gen_schema.py"


def _regen_schema() -> dict:
    runpy.run_path(str(GEN), run_name="__main__")
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _validate(data: dict, schema: dict) -> list[str]:
    validator = Draft202012Validator(schema)
    return [
        f"{'/'.join(map(str, e.path)) or '(root)'}: {e.message}"
        for e in sorted(validator.iter_errors(data), key=lambda e: e.path)
    ]


def promote(ids: list[str]) -> int:
    schema = _regen_schema()
    errors = 0

    for pid in ids:
        src = PENDING_DIR / f"{pid}.yml"
        dst = PROJECTS_DIR / f"{pid}.yml"

        if not src.exists():
            print(f"[SKIP]  {pid}: not found in data/pending/")
            errors += 1
            continue
        if dst.exists():
            print(f"[SKIP]  {pid}: already exists in data/projects/")
            errors += 1
            continue

        try:
            data = yaml.safe_load(src.read_text(encoding="utf-8")) or {}
        except Exception as e:
            print(f"[FAIL]  {pid}: YAML parse error: {e}")
            errors += 1
            continue

        # filename-to-id check
        if data.get("id") != pid:
            print(f"[FAIL]  {pid}: id field '{data.get('id')}' does not match filename")
            errors += 1
            continue

        schema_errors = _validate(data, schema)
        if schema_errors:
            print(f"[FAIL]  {pid}: schema errors (fix before promoting):")
            for e in schema_errors:
                print(f"  - {e}")
            errors += 1
            continue

        src.rename(dst)
        print(f"[OK]    {pid}: moved to data/projects/")

    return errors


def audit() -> None:
    rows = []
    for f in sorted(PENDING_DIR.glob("*.yml")):
        if f.stem.startswith("_"):
            continue
        try:
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except Exception:
            rows.append((f.stem, "PARSE ERROR", "", ""))
            continue

        notes = (d.get("notes") or "").strip()
        impl = d.get("implementation") or []
        flags = []
        if not notes:
            flags.append("no-notes")
        elif len(notes) < 30:
            flags.append("short-notes")
        if impl == ["software"]:
            flags.append("default-impl")

        quality = "needs-review" if flags else "ready"
        rows.append((f.stem, quality, ", ".join(flags), notes[:60]))

    needs = [r for r in rows if r[1] != "ready"]
    ready = [r for r in rows if r[1] == "ready"]

    print(f"Pending audit: {len(rows)} total, {len(ready)} ready, {len(needs)} need review\n")

    if ready:
        print("=== Ready to promote ===")
        for stem, _, _, notes in ready:
            print(f"  {stem:<45}  {notes}")

    if needs:
        print(f"\n=== Needs review ({len(needs)}) ===")
        for stem, _, flags, notes in needs:
            print(f"  {stem:<45}  [{flags}]  {notes}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote pending projects or audit pending quality")
    parser.add_argument("ids", nargs="*", metavar="ID", help="IDs to promote")
    parser.add_argument("--audit", action="store_true", help="Report pending file quality")
    args = parser.parse_args()

    if args.audit:
        audit()
        return

    if not args.ids:
        parser.print_help()
        sys.exit(0)

    errors = promote(args.ids)
    if errors:
        print(f"\n{errors} item(s) could not be promoted")
        sys.exit(1)
    print(f"\nPromoted {len(args.ids)} project(s) — run validate.py to confirm")


if __name__ == "__main__":
    main()
