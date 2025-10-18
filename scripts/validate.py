from __future__ import annotations

import sys
from pathlib import Path
import json
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "project.schema.json"
PROJECTS_DIR = ROOT / "data" / "projects"

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


def validate_all(schema: dict) -> int:
    validator = Draft202012Validator(schema)
    ids = set()
    errors_total = 0

    for yml in sorted(PROJECTS_DIR.glob("*.yml")):
        with yml.open("r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"[FAIL] {yml.name}: YAML parse error: {e}")
                errors_total += 1
                continue

        # duplicate id check
        pid = data.get("id")
        if not pid:
            print(f"[FAIL] {yml.name}: missing 'id'")
            errors_total += 1
        elif pid in ids:
            print(f"[FAIL] {yml.name}: duplicate id '{pid}'")
            errors_total += 1
        else:
            ids.add(pid)

        # schema validation
        errs = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if errs:
            print(f"[FAIL] {yml.name}:")
            for e in errs:
                loc = "/".join(map(str, e.path)) or "(root)"
                print(f"  - {loc}: {e.message}")
            errors_total += 1
        else:
            print(f"[OK]   {yml.name}")

    return errors_total


def main():
    run_gen_schema()
    schema = load_schema()
    errors = validate_all(schema)
    if errors:
        print(f"\n{errors} file(s) failed validation")
        sys.exit(1)
    print("\nAll project files validated")
    sys.exit(0)


if __name__ == "__main__":
    main()
