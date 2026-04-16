# ApiLens

OpenAPI snapshot tracking and visual diff for FastAPI projects.

ApiLens automatically captures versioned snapshots of your OpenAPI spec on every merge, provides a visual diff viewer, and posts PR comments summarizing what changed.

## Features

- **Automatic snapshots** — captures your spec on every merge to `main`; skips if nothing changed
- **Visual diff viewer** — color-coded UI showing new, removed, and modified endpoints with field-level detail
- **PR comments** — posts a Markdown summary of API changes on every pull request
- **AI prompts** — one-click copy of prompts to help update frontend TypeScript types
- **Zero integration** — no changes needed to your FastAPI app; runs standalone

## Install

```bash
pip install api-lens[serve]
```

## Quick Start

### 1. Create `apilens.toml`

```toml
[apilens]
app = "myapp.main:app"        # dotted path to your FastAPI app object
snapshots_dir = "openapi-snapshots"
```

### 2. Generate a snapshot manually

```bash
apilens snapshot
```

### 3. Browse the diff viewer

```bash
apilens serve
# → http://127.0.0.1:8765
```

Optionally password-protect it:

```bash
APILENS_PASSWORD=secret apilens serve
```

### 4. Add to CI

Copy the workflow templates from [`.github/workflows/`](.github/workflows/) into your repo. They require no secrets beyond the built-in `GITHUB_TOKEN`.

## CLI Reference

```
apilens generate <output>    Write the current OpenAPI spec to a JSON file
apilens snapshot             Write a snapshot (skips if spec unchanged)
apilens serve                Start the visual diff viewer
```

## Disabling the PR Comment

To temporarily disable the PR comment without deleting the workflow:

```yaml
# In .github/workflows/api-diff.yml, change:
if: github.event_name == 'pull_request'
# to:
if: false && github.event_name == 'pull_request'
```

Remove the `false &&` to re-enable.

## License

MIT
