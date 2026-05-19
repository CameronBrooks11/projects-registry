# Changelog

All notable changes to this project will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

---

## [0.2.0] — 2026-05-19

### Added
- `pyproject.toml` — ruff (lint + format) and mypy configuration targeting `scripts/`
- `.editorconfig` — consistent indent/encoding/line-ending rules across file types
- `.prettierrc` — JS/TS/JSON/YAML/Markdown formatting (100-char width, 2-space indent)
- `.pre-commit-config.yaml` — ruff, ruff-format, prettier, and standard pre-commit-hooks
- `requirements.txt` — `ruff`, `mypy`, `pre-commit` added as dev dependencies
- `package.json` — `prettier` dependency and `format` / `format:check` scripts
- `validate.py` — filename-to-id check (e.g. caught 3 mismatched filenames in `data/projects/`)
- `validate.py` — warn-only validation pass over `data/pending/` (opt-out via `--skip-pending`)
- `validate.py` — optional URL reachability check via `--check-urls` flag
- `gen_schema.py` — field-length guards: `notes` max 500 chars, `tags` max 20 items × 50 chars each
- `build.py` — `--enrich` flag fetches live GitHub stats (stars, forks, open issues, last commit, language, topics) and computes a weighted activity score; uses `GITHUB_TOKEN` if present
- `scan_github_pending.py` — `_make_session()` reads `GITHUB_TOKEN` from env for authenticated API calls (5000 req/hr vs 60)
- `.github/workflows/ci.yml` — validates `data/projects/` on every PR to `main`
- `.github/workflows/build-deploy.yml` — passes `GITHUB_TOKEN` to scan and build steps; adds `--enrich` to build; adds `git pull --rebase` before pending-stub push
- `.github/dependabot.yml` — weekly dependency updates for npm and pip

### Fixed
- Renamed `data/projects/L298N_Arduino.yml` → `l298n-arduino.yml` (id mismatch)
- Renamed `data/projects/LMD18200_Arduino.yml` → `lmd18200-arduino.yml` (id mismatch)
- Renamed `data/projects/uwo-fast-github-io.yml` → `uwo-fast-gh-pages.yml` (id mismatch)

---

## [0.1.0] — 2026-05-15

### Added
- Initial MVP: taxonomy-driven YAML project registry with VitePress site
- `data/taxonomy.yml` — authoritative enum definitions for all classification fields
- `schema/project.schema.json` — generated from taxonomy via `gen_schema.py`
- `scripts/validate.py` — schema validation and duplicate-id check for `data/projects/`
- `scripts/build.py` — collects projects into `dist/projects-index.json` and injects into VitePress theme
- `scripts/scan_github_pending.py` — auto-discovers public repos from configured GitHub users/orgs
- `scripts/gen_schema.py` — generates JSON Schema from taxonomy
- `.github/workflows/build-deploy.yml` — daily scan, validate, build, and deploy to GitHub Pages
