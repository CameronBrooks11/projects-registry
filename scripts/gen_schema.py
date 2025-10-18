from __future__ import annotations

import json
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
TAX_PATH = ROOT / "data" / "taxonomy.yml"
SCHEMA_PATH = ROOT / "schema" / "project.schema.json"

REQUIRED_TAX_KEYS = [
    "types",
    "implementation",
    "artifact",
    "target",
    "maturity",
    "status",
]


def load_taxonomy(path: Path) -> dict:
    if not path.exists():
        sys.stderr.write(f"ERROR: taxonomy not found: {path}\n")
        sys.exit(1)
    with path.open("r", encoding="utf-8") as f:
        tax = yaml.safe_load(f)
    for k in REQUIRED_TAX_KEYS:
        if k not in tax or not isinstance(tax[k], list):
            sys.stderr.write(f"ERROR: taxonomy missing list: {k}\n")
            sys.exit(1)
    return tax


def build_schema(tax: dict) -> dict:
    # JSON Schema, enums sourced from taxonomy.yml
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Project",
        "type": "object",
        "required": ["id", "name", "type"],
        "additionalProperties": False,
        "properties": {
            "id": {"type": "string", "pattern": "^[a-z0-9-]+$"},
            "name": {"type": "string", "minLength": 1},
            "type": {"type": "string", "enum": tax["types"]},
            "implementation": {
                "type": "array",
                "items": {"type": "string", "enum": tax["implementation"]},
                "uniqueItems": True,
            },
            "artifact": {
                "type": "array",
                "items": {"type": "string", "enum": tax["artifact"]},
                "uniqueItems": True,
            },
            "target": {
                "type": "array",
                "items": {"type": "string", "enum": tax["target"]},
                "uniqueItems": True,
            },
            "maturity": {"type": "string", "enum": tax["maturity"]},
            "status": {"type": "string", "enum": tax["status"]},
            "repos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["host", "url"],
                    "additionalProperties": False,
                    "properties": {
                        "host": {
                            "type": "string",
                            "enum": ["github", "gitlab", "other"],
                        },
                        "url": {"type": "string", "format": "uri"},
                    },
                },
            },
            "links": {
                "type": "object",
                "additionalProperties": True,
                "properties": {
                    "docs": {"type": "string", "format": "uri"},
                    "issues": {"type": "string", "format": "uri"},
                    "site": {"type": "string", "format": "uri"},
                },
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "uniqueItems": True,
            },
            "notes": {"type": "string"},
        },
    }


def main():
    tax = load_taxonomy(TAX_PATH)
    schema = build_schema(tax)
    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SCHEMA_PATH.open("w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    print(f"Schema written: {SCHEMA_PATH}")


if __name__ == "__main__":
    main()
