from __future__ import annotations

import json
from pathlib import Path
import sys
import yaml
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "data" / "projects"
PENDING_DIR = ROOT / "data" / "pending"
TAX_PATH = ROOT / "data" / "taxonomy.yml"
DIST_DIR = ROOT / "dist"
PROJECTS_INDEX_PATH = DIST_DIR / "projects-index.json"
PENDING_INDEX_PATH = DIST_DIR / "pending-index.json"
THEME_DIR = ROOT / "site" / ".vitepress" / "theme"
THEME_PROJECTS_INDEX_PATH = THEME_DIR / "projects-index.json"
THEME_PENDING_INDEX_PATH = THEME_DIR / "pending-index.json"


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def slugify(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in s).strip("-")


def coerce_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def main():
    if not TAX_PATH.exists():
        sys.stderr.write(f"ERROR: taxonomy not found: {TAX_PATH}\n")
        sys.exit(1)
    taxonomy = load_yaml(TAX_PATH)

    # Process main projects
    projects = []
    for yml in sorted(PROJECTS_DIR.glob("*.yml")):
        data = load_yaml(yml)
        if yml.name.startswith("_"):
            # allow template files in the folder
            continue

        pid = data.get("id")
        name = data.get("name", "")
        if not pid or not name:
            sys.stderr.write(f"SKIP {yml.name}: missing id or name\n")
            continue

        # normalize
        rec = {
            "id": pid,
            "name": name,
            "slug": slugify(pid),
            "type": data.get("type"),
            "implementation": coerce_list(data.get("implementation")),
            "artifact": coerce_list(data.get("artifact")),
            "target": coerce_list(data.get("target")),
            "maturity": data.get("maturity"),
            "status": data.get("status"),
            "repos": data.get("repos", []),
            "links": data.get("links", {}),
            "tags": coerce_list(data.get("tags")),
            "notes": data.get("notes", ""),
            # derived placeholders (filled by future enrich step)
            "derived": {
                "stars": None,
                "forks": None,
                "open_issues": None,
                "last_commit": None,
                "primary_language": None,
                "topics": [],
                "activity_score": None,
            },
        }
        projects.append(rec)

    # Process pending projects (simplified structure)
    pending = []
    if PENDING_DIR.exists():
        for yml in sorted(PENDING_DIR.glob("*.yml")):
            data = load_yaml(yml)
            if yml.name.startswith("_"):
                continue

            pid = data.get("id")
            name = data.get("name", "")
            if not pid or not name:
                sys.stderr.write(f"SKIP pending {yml.name}: missing id or name\n")
                continue

            # Simplified record for pending projects
            rec = {
                "id": pid,
                "name": name,
                "notes": data.get("notes", ""),
                "repos": data.get("repos", []),
            }
            pending.append(rec)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    THEME_DIR.mkdir(parents=True, exist_ok=True)

    # Shared metadata
    generated_at = (
        datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    )
    taxonomy_data = {
        k: v
        for k, v in taxonomy.items()
        if k in ("types", "implementation", "artifact", "target", "maturity", "status")
    }

    # Create projects payload
    projects_payload = {
        "generated_at": generated_at,
        "count": len(projects),
        "projects": projects,
        "taxonomy": taxonomy_data,
    }

    # Create pending payload
    pending_payload = {
        "generated_at": generated_at,
        "count": len(pending),
        "pending": pending,
    }

    # Write projects files
    PROJECTS_INDEX_PATH.write_text(
        json.dumps(projects_payload, indent=2), encoding="utf-8"
    )
    THEME_PROJECTS_INDEX_PATH.write_text(
        json.dumps(projects_payload, indent=2), encoding="utf-8"
    )

    # Write pending files
    PENDING_INDEX_PATH.write_text(
        json.dumps(pending_payload, indent=2), encoding="utf-8"
    )
    THEME_PENDING_INDEX_PATH.write_text(
        json.dumps(pending_payload, indent=2), encoding="utf-8"
    )

    print(f"Wrote {PROJECTS_INDEX_PATH} ({len(projects)} projects)")
    print(f"Wrote {THEME_PROJECTS_INDEX_PATH} ({len(projects)} projects)")
    print(f"Wrote {PENDING_INDEX_PATH} ({len(pending)} pending)")
    print(f"Wrote {THEME_PENDING_INDEX_PATH} ({len(pending)} pending)")


if __name__ == "__main__":
    main()
