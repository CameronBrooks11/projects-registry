# Projects Registry

Data-driven open source project index built with VitePress.

## Architecture

- **Data layer** — `data/taxonomy.yml` defines controlled vocabularies (types, implementation, artifact, target, maturity, status). One YAML file per project in `data/projects/`; unreviewed stubs land in `data/pending/`.
- **Build layer** — `scripts/gen_schema.py` generates `schema/project.schema.json` from taxonomy. `scripts/validate.py` validates all project files. `scripts/build.py` assembles `dist/projects-index.json` (with optional `--enrich` for live GitHub stats). `scripts/promote.py` moves reviewed stubs from pending to projects.
- **Site layer** — VitePress imports the built index. `<ProjectList />` and `<FilterBar />` render client-side filtering and sorting.
- **CI/CD** — GitHub Actions: validate → build dataset → build site → deploy to Pages on every push to `main` and on a daily schedule.

## Local workflow

```sh
# Install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
npm install

# Validate data
python scripts/validate.py

# Build dataset (add --enrich for live GitHub stats; needs GITHUB_TOKEN)
python scripts/build.py

# Dev server
npm run dev

# Production build + preview
npm run build && npm run serve
```

## Data contract

| Field | Required | Notes |
|---|---|---|
| `id` | ✓ | kebab-case, unique |
| `name` | ✓ | display name |
| `type` | ✓ | from taxonomy |
| `implementation[]` | recommended | from taxonomy |
| `artifact[]` | recommended | from taxonomy |
| `target[]` | recommended | from taxonomy |
| `maturity` | recommended | from taxonomy |
| `status` | recommended | from taxonomy |
| `repos[]` | optional | `{host, url}` pairs |
| `links{}` | optional | `docs`, `site`, `issues` |
| `tags[]` | optional | free-form |
| `notes` | optional | max 500 chars |

All enumerations are sourced from `data/taxonomy.yml`. Unknown keys are rejected by the schema.
