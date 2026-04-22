# ApiLens

Automatically generate versioned API snapshots on every merge. Explore changes between any two versions in a UI with color-coded diff highlighting. Built for FastAPI + TypeScript teams.

[https://pypi.org/project/openapi-lens/](https://pypi.org/project/openapi-lens/)

---

## How It Works

1. Every time code merges to `main`, a GitHub Actions workflow imports your FastAPI app, generates its OpenAPI spec, and compares it to the previous snapshot. If anything changed, it commits a new snapshot file to your repo under `openapi-snapshots/`. The `openapi-snapshots/` folder is created automatically by the workflow on first run.
2. On every pull request, a second workflow computes the diff between the PR branch and the latest snapshot, and posts a comment summarizing what changed (comment can be disabled).
3. Install the PyPi package (openapi-lens), then locally run `apilens serve` to browse and compare any two snapshots in a visual UI. Optionally, add a few lines to deploy the viewer alongside your app.

---

## Features

- **Automatic snapshots** — captures your spec on every merge to `main`; skips if nothing changed
- **Visual diff viewer** — color-coded UI showing new, removed, and modified endpoints with field-level detail
- **PR comments** — posts a Markdown summary of API changes on every pull request
- **AI prompts** — one-click copy of prompts to help update frontend TypeScript types
- **Zero integration** — no changes to your FastAPI app; runs completely standalone

---

## Requirements

Python 3.10 or higher. Check yours with:

```bash
python3 --version
```

---

## Setup

### 1. Install

```bash
pip3 install "openapi-lens[serve]"
```

### 2. Copy `apilens.toml` into your project root

Grab `[apilens.toml](apilens.toml)` from this repo and place it at the root of your project. Edit one line:

```toml
[apilens]
app = "myapp.main:app"   # ← change this to your FastAPI app's import path
```

### 3. Copy the workflow files into your `.github/workflows/`

Grab both files from `[workflow-templates/](workflow-templates/)`:

- `**openapi-snapshot.yml**` — on every push to `main`, generates your spec and commits a new snapshot to `openapi-snapshots/` if anything changed
- `**api-diff.yml**` — on every PR, posts a comment showing exactly what endpoints and fields changed



> **Set your app path:** both workflow files have an `APP_PATH` env var near the top of the job. Set it to the directory containing your FastAPI app's `setup.py` or `pyproject.toml` before committing:
>
> ```yaml
> env:
>   APP_PATH: ./backend  # ← change to your FastAPI app's directory
> ```
>
> This is the only line you need to change in each workflow file.

### 4. Push to your repo

Commit and push the three files (`apilens.toml`, `openapi-snapshot.yml`, `api-diff.yml`). From this point:

- **On the next merge to `main`** — the snapshot workflow fires automatically. It imports your app, generates the spec, and commits the first `openapi-snapshots/<timestamp>.json` file to your repo. You can watch it run in your repo's Actions tab.
- **On every subsequent PR** — the diff workflow fires automatically and posts a comment to the PR showing what changed.

You don't need to do anything else to keep snapshots running, it's fully automatic from here.

### 5. Browse snapshots

Once at least two snapshots exist in your repo, pull the latest changes and choose one of the two options below.

> **Note:** the dropdowns will be empty until at least one snapshot exists. You need at least two snapshots to compare — meaning two separate merges to `main` that each changed the API.

#### Option A — Local only

Run from your project root:

```bash
apilens serve
```

This starts the viewer at `http://127.0.0.1:8765`, visible only on your machine. ApiLens reads the `snapshots_dir` from your `apilens.toml` automatically.

#### Option B — Mount inside your FastAPI app (recommended for teams)

If you want the viewer deployed alongside your app so your whole team can access it, add these lines to your `main.py`:

```python
import os
from apilens.viewer.app import mount

mount(app, path="/apilens", password=os.environ.get("APILENS_PASSWORD"))
```

Then set `APILENS_PASSWORD` in your server's environment variables. The viewer will be available at `yourapp.com/apilens` and anyone visiting it will be prompted for the password.

---

## Disabling PR Comments

If you want to disable the PR comments, set `pr_comments = false` in your `apilens.toml`:

```toml
[apilens]
pr_comments = false
```

---

## License

MIT