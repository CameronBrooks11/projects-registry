# Project Gaps (temp)

## ~~Phase 1 — Tooling Foundation~~ ✓
- ~~Python: no `ruff`, `black`, `mypy`, or `pyproject.toml`~~ → added `pyproject.toml` with ruff + mypy config
- ~~JS/Markdown: no `prettier`, `.editorconfig`, or `eslint`~~ → added `.prettierrc`, `.editorconfig`; prettier added to `package.json`
- ~~No `.pre-commit-config.yaml`~~ → added with ruff, ruff-format, prettier, and pre-commit-hooks

## Phase 2 — Data Integrity
- `validate.py` does not verify that the YAML filename matches the `id` field inside the file
- `validate.py` does not validate `data/pending/` — only `data/projects/`
- No URL reachability checks for `repos` / `links` fields
- No field-length guards on `notes` or `tags`

## Phase 3 — Build Enrichment
- `build.py`: derived data (GitHub stars, activity score, last commit date) is stubbed out but not implemented

## Phase 4 — CI/CD
- `scan_github_pending.py` makes unauthenticated GitHub API calls (60 req/hr limit); `GITHUB_TOKEN` is available in the runner but not passed to the script
- Scan job commits auto-generated pending stubs directly to `main` (race-condition-prone, noisy history)
- No PR preview/staging workflow; site only deploys on push to `main`

## Phase 5 — Housekeeping
- No `.github/dependabot.yml` — npm and pip dependencies are unmonitored
- No `CHANGELOG.md`

## Phase 6 — Data Cleanup
- `data/projects/` — 14 files, consistent and schema-compliant
- `data/pending/` — ~180 auto-generated stubs; many have low-quality `notes` (raw GitHub descriptions) and need manual review before promotion to `projects/`
