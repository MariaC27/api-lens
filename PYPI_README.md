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
pip3 install "openapi-lens[serve]"
```

## Usage

```bash
apilens serve
```

The viewer requires snapshots to be generated via GitHub Actions workflows. For full setup instructions, workflow templates, and configuration, see the [GitHub repository](https://github.com/MariaC27/api-lens).

## License

MIT
