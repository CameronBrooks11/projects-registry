#!/usr/bin/env python3
"""
Scan GitHub sources (users/orgs) defined in data/github_scan.yml
and generate pending project stubs in data/pending/.
No GitHub token required.
"""

import pathlib
import re
import sys
import time

import requests
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CONFIG_FILE = DATA_DIR / "github_scan.yml"
PROJECTS_DIR = DATA_DIR / "projects"
PENDING_DIR = DATA_DIR / "pending"
TEMPLATE_FILE = PROJECTS_DIR / "_template.project.yml"

API = "https://api.github.com"
PENDING_DIR.mkdir(parents=True, exist_ok=True)


# -------------------- utils --------------------


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def save_yaml(path, data):
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )


def kebab(s):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.strip().lower())
    return s.strip("-")


def gh_paged(url):
    page = 1
    while True:
        r = requests.get(url, params={"per_page": 100, "page": page})
        if r.status_code != 200:
            break
        items = r.json()
        if not items:
            break
        yield from items
        if 'rel="next"' not in r.headers.get("Link", ""):
            break
        page += 1
        time.sleep(0.2)  # be gentle


def load_existing_urls():
    urls = set()
    for d in [PROJECTS_DIR, PENDING_DIR]:
        if not d.exists():
            continue
        for f in d.glob("*.yml"):
            try:
                y = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
                for repo in y.get("repos", []):
                    u = repo.get("url")
                    if u:
                        urls.add(u)
            except Exception:
                pass
    return urls


def repo_to_pending(repo, template, owner_name):
    """Convert a GitHub repo into a pending project entry."""
    name = repo["name"]
    rid = kebab(f"{owner_name}-{name}")  # prevent collisions across orgs/users
    url = repo["html_url"]
    desc = repo.get("description") or ""
    data = dict(template)
    data.update(
        {
            "id": rid,
            "name": name,
            "repos": [{"host": "github", "url": url}],
            "notes": desc.strip(),
            "status": "active",
            "maturity": "prototype",
            "implementation": ["software"],
            "links": {
                "issues": f"{url}/issues",
                "docs": repo.get("homepage") or "",
            },
        }
    )
    return data


# -------------------- main --------------------


def main():
    if not CONFIG_FILE.exists():
        print("Missing config:", CONFIG_FILE)
        sys.exit(1)

    cfg = load_yaml(CONFIG_FILE)
    defaults = cfg.get("defaults", {})
    sources = cfg.get("sources", [])
    template = load_yaml(TEMPLATE_FILE)
    existing = load_existing_urls()
    new_files = []

    for src in sources:
        stype = src.get("type")
        name = src.get("name")
        if not stype or not name:
            continue

        inc_forks = src.get("include_forks", defaults.get("include_forks", False))
        inc_arch = src.get("include_archived", defaults.get("include_archived", False))
        blacklist = set([b.lower() for b in src.get("blacklist", [])])

        if stype == "user":
            url = f"{API}/users/{name}/repos?type=public&sort=updated"
        elif stype == "org":
            url = f"{API}/orgs/{name}/repos?type=public&sort=updated"
        else:
            continue

        print(f"Scanning {stype}:{name} (forks={inc_forks}, archived={inc_arch})")

        for repo in gh_paged(url):
            html = repo["html_url"]
            rname = repo["name"].lower()
            if not inc_forks and repo.get("fork"):
                continue
            if not inc_arch and repo.get("archived"):
                continue
            if repo.get("private"):
                continue
            # blacklist check (by name or full URL)
            if rname in blacklist or html.lower() in blacklist:
                continue
            if html in existing:
                continue

            data = repo_to_pending(repo, template, name)
            out = PENDING_DIR / f"{data['id']}.yml"
            if out.exists():
                continue
            save_yaml(out, data)
            new_files.append(out.name)

    if new_files:
        print(f"✅ Added {len(new_files)} pending repos:")
        for n in sorted(new_files):
            print("  -", n)
    else:
        print("No new repos added.")


if __name__ == "__main__":
    main()
