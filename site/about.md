# About

**Projects Registry** is a structured, data-driven index of open-source and open-hardware projects.
Each entry is a YAML file classified against a shared taxonomy so the whole catalog stays searchable,
filterable, and machine-readable.

## How it works

```
GitHub scan  -->  data/pending/  -->  manual review  -->  data/projects/  -->  dist/  -->  site
```

1. **Automated discovery** - a daily GitHub Actions workflow scans configured accounts and creates
   stub entries in `data/pending/` for any new public repositories.
2. **Classification** - each stub is reviewed and classified against the taxonomy: `type`,
   `implementation`, `artifact`, `target`, `maturity`, `status`, and optional `tags`/`notes`.
3. **Validation** - `scripts/validate.py` checks every entry against the generated JSON Schema
   and enforces filename-to-id consistency.
4. **Promotion** - reviewed entries are moved to `data/projects/` via `scripts/promote.py`.
5. **Build** - `scripts/build.py` aggregates all projects into `dist/projects-index.json`,
   optionally enriching entries with live GitHub stats (stars, forks, last commit, activity score).
6. **Deploy** - VitePress builds the site and deploys to GitHub Pages on every push to `main`.

## Taxonomy

Projects are classified along four axes:

| Field | Cardinality | Description |
|---|---|---|
| `type` | exactly one | What the project fundamentally *is* (system, machine, component, part, ...) |
| `implementation` | zero or more | Where the main technical work lives (hardware, firmware, software) |
| `artifact` | zero or more | Primary form of deliverables (design, documentation, dataset, ...) |
| `target` | zero or more | Where it runs or is deployed (mcu, pc, browser, cloud, ...) |

Full vocabulary is defined in [`data/taxonomy.yml`](https://github.com/CameronBrooks11/projects-registry/blob/main/data/taxonomy.yml).

## Contributing

To add a project:

1. Create a YAML file in `data/pending/` following the schema in `schema/project.schema.json`.
2. Run `python scripts/validate.py` locally to confirm it passes.
3. Open a pull request - CI will validate automatically.

To promote a pending entry after review:

```bash
python scripts/promote.py <project-id>
```

## Source

[github.com/CameronBrooks11/projects-registry](https://github.com/CameronBrooks11/projects-registry)

