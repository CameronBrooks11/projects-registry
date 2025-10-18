# Projects Registry — Technical Notes

Goal

- Single-source registry of projects with automated validation, build, and site publish.
- Humans edit only taxonomy and project records. Everything else is derived.

Scope

- Public, data-driven catalog of systems, machines, components, software, docs, etc.
- Minimal moving parts; predictable builds; static hosting on GitHub Pages.

Architecture

- Data layer (authoritative)
  - `data/taxonomy.yml` — controlled vocabularies (types, implementation, artifact, target, maturity, status).
  - `data/projects/*.yml` — one file per project using `_template.project.yml`.
- Build layer (automated)
  - `scripts/gen_schema.py` — generates JSON Schema from taxonomy (no duplicated enums).
  - `scripts/validate.py` — validates all project files, enforces uniqueness and shape.
  - `scripts/build.py` — normalizes records and emits `dist/index.json` (+ taxonomy snapshot).
  - (Future) `scripts/adapters/github_pull.py` — enriches with repo stats and topics, cached.
- Site layer
  - VitePress app imports `dist/index.json` at build/dev time.
  - `<ProjectList />` + `<FilterBar />` render client-side filtering and sorting.
  - Theme registers components via `site/.vitepress/theme/index.ts`.
- CI/CD
  - GitHub Actions: validate → build dataset → build site → deploy to Pages.
  - Secrets: `GH_TOKEN` (future enrichment).

Separation of Concerns

- Manual: taxonomy updates, new/edited project YAML.
- Automated: schema sync, validation, dataset assembly, site rendering, deploy.

Data Contract (project file)

- Required: `id`, `name`, `type`
- Recommended: `implementation[]`, `artifact[]`, `target[]`, `maturity`, `status`
- Optional: `repos[]`, `links{}`, `tags[]`, `notes`
- All enumerations sourced from `data/taxonomy.yml`.

Conventions

- `id`: kebab-case, unique across the registry.
- One project per YAML file. Do not include derived fields.
- Unknown keys are rejected by schema.

Workflow (local)

- Validate, build dataset, run site, verify filters, then commit and push.

Release Process

- Every push to `main` runs CI.
- Fail fast on schema violations; Pages deploys only from green builds.

Roadmap

- Repo enrichment (GitHub GraphQL) with ETag caching.
- `dist/search.json` for client search.
- Org scanners to prefill `repos` from known orgs.
- Summary analytics in `dist/summary.json`.

File Map

- See repo root for `data/`, `scripts/`, `dist/`, `site/`, `.github/workflows/`.

Local commands:

```sh
# 1) Validate schema and data
python scripts/validate.py

# 2) Build dataset
python scripts/build.py

# 3) Dev server (from repo root)
npm install
npm run dev
# Open the Local URL shown

# 4) Production build and preview
npm run build
npm run serve
```
