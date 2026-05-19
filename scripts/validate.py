from __future__ import annotations

import argparse
import sys
from pathlib import Path
import json
import yaml
import requests
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "project.schema.json"
PROJECTS_DIR = ROOT / "data" / "projects"
PENDING_DIR = ROOT / "data" / "pending"

# Import generator without relative import tricks
GEN = ROOT / "scripts" / "gen_schema.py"
if not GEN.exists():
    sys.stderr.write("ERROR: gen_schema.py not found\n")
    sys.exit(1)


def run_gen_schema():
    # Execute the generator in a child process to avoid path/module issues
    import runpy

    runpy.run_path(str(GEN), run_name="__main__")


def load_schema():
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_all(schema: dict, directory: Path, strict: bool = True) -> int:
    validator = Draft202012Validator(schema)
    ids: set[str] = set()
    errors_total = 0

    for yml in sorted(directory.glob("*.yml")):
        if yml.stem.startswith("_"):
            continue  # skip templates

        with yml.open("r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"[FAIL] {yml.name}: YAML parse error: {e}")
                errors_total += 1
                continue

        file_errors = 0

        # filename-to-id check
        pid = data.get("id")
        if pid and yml.stem != pid:
            msg = f"filename '{yml.stem}' does not match id '{pid}'"
            if strict:
                print(f"[FAIL] {yml.name}: {msg}")
                file_errors += 1
            else:
                print(f"[WARN] {yml.name}: {msg}")

        # duplicate id check
        if not pid:
            print(f"[FAIL] {yml.name}: missing 'id'")
            file_errors += 1
        elif pid in ids:
            print(f"[FAIL] {yml.name}: duplicate id '{pid}'")
            file_errors += 1
        else:
            ids.add(pid)

        # schema validation
        errs = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if errs:
            label = "[FAIL]" if strict else "[WARN]"
            print(f"{label} {yml.name}:")
            for e in errs:
                loc = "/".join(map(str, e.path)) or "(root)"
                print(f"  - {loc}: {e.message}")
            if strict:
                file_errors += 1
        elif file_errors == 0:
            print(f"[OK]   {yml.name}")

        if strict:
            errors_total += file_errors

    return errors_total


def _collect_urls(directory: Path) -> list[tuple[str, str]]:
    """Return [(filename, url), ...] for all non-empty URLs in a directory."""
    results = []
    for yml in sorted(directory.glob("*.yml")):
        if yml.stem.startswith("_"):
            continue
        try:
            data = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        for repo in data.get("repos") or []:
            u = repo.get("url", "")
            if u:
                results.append((yml.name, u))
        for u in (data.get("links") or {}).values():
            if u:
                results.append((yml.name, u))
    return results


def check_urls(directory: Path) -> int:
    errors = 0
    for filename, url in _collect_urls(directory):
        try:
            r = requests.head(url, timeout=10, allow_redirects=True)
            if r.status_code >= 400:
                print(f"[URL-FAIL] {filename}: {url} → HTTP {r.status_code}")
                errors += 1
            else:
                print(f"[URL-OK]   {filename}: {url}")
        except requests.RequestException as exc:
            print(f"[URL-FAIL] {filename}: {url} → {exc}")
            errors += 1
    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate project YAML files")
    parser.add_argument(
        "--check-urls",
        action="store_true",
        help="Check URL reachability for projects/ (slow, makes network requests)",
    )
    parser.add_argument(
        "--skip-pending",
        action="store_true",
        help="Skip warn-only validation of data/pending/",
    )
    args = parser.parse_args()

    run_gen_schema()
    schema = load_schema()

    print("=== Validating projects/ ===")
    errors = validate_all(schema, PROJECTS_DIR, strict=True)

    if not args.skip_pending:
        print("\n=== Validating pending/ (warn-only) ===")
        validate_all(schema, PENDING_DIR, strict=False)

    if args.check_urls:
        print("\n=== Checking URLs in projects/ ===")
        errors += check_urls(PROJECTS_DIR)

    if errors:
        print(f"\n{errors} file(s) failed validation")
        sys.exit(1)
    print("\nAll project files validated")
    sys.exit(0)


if __name__ == "__main__":
    main()
