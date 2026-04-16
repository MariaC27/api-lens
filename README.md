# ApiLens

Automatically generate versioned API snapshots on every merge. Explore changes between any two versions in a UI with color-coded diff highlighting. Built for FastAPI + TypeScript teams.

## Features

- **Automatic snapshots** — captures your spec on every merge to `main`; skips if nothing changed
- **Visual diff viewer** — color-coded UI showing new, removed, and modified endpoints with field-level detail
- **PR comments** — posts a Markdown summary of API changes on every pull request
- **AI prompts** — one-click copy of prompts to help update frontend TypeScript types
- **Zero integration** — no changes to your FastAPI app; runs completely standalone

## Install

```bash
pip install openapi-lens[serve]
```

## Setup

### 1. Add the config and workflow files

**1a.** Copy [`apilens.toml`](apilens.toml) into your project root. Set `app` to the dotted import path of your FastAPI app (e.g. `myapp.main:app` — same as you'd pass to `uvicorn`). No secrets, safe to commit.

**1b.** Copy the two workflow files from [`workflow-templates/`](workflow-templates/) into your `.github/workflows/`:

- **`openapi-snapshot.yml`** — runs on every push to `main`. Generates your OpenAPI spec, compares it to the last snapshot, and commits a new one only if something changed.
- **`api-diff.yml`** — runs on every PR. Posts a comment showing exactly what endpoints and fields changed.

Both workflows use the built-in `GITHUB_TOKEN` — no secrets to configure.

### 3. Browse the diff viewer locally

```bash
apilens serve
# → http://127.0.0.1:8765
```

Point it at any repo that has an `openapi-snapshots/` directory. Optionally password-protect it:

```bash
APILENS_PASSWORD=secret apilens serve
```

## CLI Reference

```
apilens generate <output>    Write the current OpenAPI spec to a JSON file
apilens snapshot             Write a snapshot (skips if spec unchanged)
apilens serve                Start the visual diff viewer
```

## Disabling the PR Comment

To temporarily disable without deleting the workflow, add `false &&` to the `if:` condition in `api-diff.yml`:

```yaml
if: false && github.event_name == 'pull_request'
```

Remove the `false &&` to re-enable.

## License

MIT
