from __future__ import annotations

import json
import math
import os
import re
import time
from pathlib import Path
import sys
import yaml
from datetime import datetime, timezone

import requests

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


# ──────────────────────────────────────────────
# GitHub enrichment
# ──────────────────────────────────────────────

_GH_SLUG_RE = re.compile(
    r"https?://github\.com/([^/]+)/([^/?#]+?)(?:\.git)?/?$"
)


def _gh_headers() -> dict[str, str]:
    headers: dict[str, str] = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _parse_gh_slug(url: str) -> tuple[str, str] | None:
    m = _GH_SLUG_RE.match(url)
    return (m.group(1), m.group(2)) if m else None


def _activity_score(stars: int, forks: int, last_commit_iso: str | None) -> float:
    """Weighted score: stars + 2×forks + recency bonus (0–50, half-life 1 year)."""
    score = float(stars + 2 * forks)
    if last_commit_iso:
        try:
            last = datetime.fromisoformat(last_commit_iso.replace("Z", "+00:00"))
            days = max((datetime.now(timezone.utc) - last).days, 0)
            score += 50 * math.exp(-days / 365)
        except Exception:
            pass
    return round(score, 2)


def _enrich_one(rec: dict, session: requests.Session) -> None:
    """Fetch live GitHub stats for a single project record and update rec['derived']."""
    gh_url = next(
        (r["url"] for r in rec.get("repos", []) if r.get("host") == "github"),
        None,
    )
    if not gh_url:
        return
    slug = _parse_gh_slug(gh_url)
    if not slug:
        return

    owner, repo = slug
    api = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        r = session.get(api, timeout=15)
        if r.status_code != 200:
            sys.stderr.write(f"  [enrich] {owner}/{repo}: HTTP {r.status_code}\n")
            return
        d = r.json()

        stars: int = d.get("stargazers_count", 0)
        forks: int = d.get("forks_count", 0)
        open_issues: int = d.get("open_issues_count", 0)
        language: str | None = d.get("language")
        topics: list[str] = d.get("topics", [])

        # most recent commit date
        last_commit: str | None = None
        cr = session.get(f"{api}/commits", params={"per_page": 1}, timeout=15)
        if cr.status_code == 200:
            commits = cr.json()
            if commits:
                last_commit = commits[0]["commit"]["author"]["date"]

        rec["derived"].update(
            {
                "stars": stars,
                "forks": forks,
                "open_issues": open_issues,
                "last_commit": last_commit,
                "primary_language": language,
                "topics": topics,
                "activity_score": _activity_score(stars, forks, last_commit),
            }
        )
        time.sleep(0.1)  # stay well within rate limits

    except requests.RequestException as exc:
        sys.stderr.write(f"  [enrich] {owner}/{repo}: {exc}\n")


def enrich_all(projects: list[dict]) -> None:
    session = requests.Session()
    session.headers.update(_gh_headers())
    token_present = bool(os.environ.get("GITHUB_TOKEN"))
    limit = "5000/hr (authenticated)" if token_present else "60/hr (unauthenticated)"
    print(f"Enriching {len(projects)} projects (rate limit: {limit})")
    for rec in projects:
        _enrich_one(rec, session)
        d = rec["derived"]
        print(
            f"  {rec['id']}: stars={d['stars']} forks={d['forks']}"
            f" last_commit={d['last_commit']} score={d['activity_score']}"
        )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Build project index JSON files")
    parser.add_argument(
        "--enrich",
        action="store_true",
        help="Fetch live GitHub stats (stars, forks, last commit) for each project",
    )
    args = parser.parse_args()

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
            # derived data — populated by enrich_all() when --enrich is passed
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

    if args.enrich:
        enrich_all(projects)

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
