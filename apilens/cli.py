# ABOUTME: Click CLI providing `apilens generate`, `apilens snapshot`, and `apilens serve`.
# ABOUTME: Entry point registered as `apilens` in pyproject.toml.

from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

import click

from apilens import config as cfg
from apilens import snapshot as snapshot_io


def _load_app(app_path: str):
    """Import the FastAPI app object from a dotted path like 'myapp.main:app'."""
    if ":" not in app_path:
        raise click.ClickException(
            f"Invalid app path '{app_path}'. Expected format: 'module.path:attribute'"
        )
    module_path, _, attr = app_path.rpartition(":")
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise click.ClickException(f"Could not import module '{module_path}': {e}")
    app = getattr(module, attr, None)
    if app is None:
        raise click.ClickException(
            f"Module '{module_path}' has no attribute '{attr}'"
        )
    return app


@click.group()
def cli():
    """ApiLens — OpenAPI snapshot and diff tool."""


@cli.command()
@click.argument("output", type=click.Path())
@click.option("--app", default=None, help="Dotted path to FastAPI app (overrides apilens.toml)")
@click.option("--config", default=None, type=click.Path(), help="Path to apilens.toml")
def generate(output: str, app: str | None, config: str | None):
    """Generate the current OpenAPI spec to OUTPUT file."""
    conf = cfg.load(Path(config) if config else None)
    app_path = app or conf.app
    if not app_path:
        raise click.ClickException(
            "No app specified. Set 'app' in apilens.toml or pass --app."
        )
    fastapi_app = _load_app(app_path)
    spec = fastapi_app.openapi()
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(spec, f, indent=2)
    click.echo(f"OpenAPI spec written to {out}")


@cli.command()
@click.option("--app", default=None, help="Dotted path to FastAPI app (overrides apilens.toml)")
@click.option("--config", default=None, type=click.Path(), help="Path to apilens.toml")
@click.option("--commit-sha", default="", envvar="GITHUB_SHA", help="Commit SHA")
@click.option("--commit-message", default="", envvar="COMMIT_MESSAGE", help="Commit message")
def snapshot(app: str | None, config: str | None, commit_sha: str, commit_message: str):
    """Generate a snapshot of the current OpenAPI spec.

    Skips writing if the spec has not changed since the last snapshot.
    """
    conf = cfg.load(Path(config) if config else None)
    app_path = app or conf.app
    if not app_path:
        raise click.ClickException(
            "No app specified. Set 'app' in apilens.toml or pass --app."
        )
    fastapi_app = _load_app(app_path)
    spec = fastapi_app.openapi()

    path = snapshot_io.write_snapshot(
        snapshots_dir=conf.snapshots_dir,
        spec=spec,
        commit_sha=commit_sha,
        commit_message=commit_message,
    )
    if path is None:
        click.echo("No API changes detected — snapshot skipped.")
        # Signal to CI that nothing changed
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                f.write("changed=false\n")
    else:
        click.echo(f"Snapshot written to {path}")
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                f.write("changed=true\n")


@cli.command()
@click.option("--config", default=None, type=click.Path(), help="Path to apilens.toml")
@click.option("--snapshots-dir", default=None, type=click.Path(), help="Snapshots directory")
@click.option("--host", default=None, help="Bind host (default: 127.0.0.1)")
@click.option("--port", default=None, type=int, help="Bind port (default: 8765)")
@click.option("--password", default=None, envvar="APILENS_PASSWORD", help="Optional Basic Auth password")
def serve(
    config: str | None,
    snapshots_dir: str | None,
    host: str | None,
    port: int | None,
    password: str | None,
):
    """Start the ApiLens diff viewer."""
    try:
        import uvicorn
    except ImportError:
        raise click.ClickException(
            "uvicorn is required for `apilens serve`. Install it with: pip install uvicorn"
        )

    conf = cfg.load(Path(config) if config else None)
    resolved_dir = Path(snapshots_dir) if snapshots_dir else conf.snapshots_dir
    resolved_host = host or conf.host
    resolved_port = port or conf.port

    if not resolved_dir.exists():
        click.echo(
            f"Warning: snapshots directory '{resolved_dir}' does not exist yet.",
            err=True,
        )

    from apilens.viewer.app import _make_app

    app = _make_app(snapshots_dir=resolved_dir, password=password)
    click.echo(f"ApiLens viewer running at http://{resolved_host}:{resolved_port}")
    uvicorn.run(app, host=resolved_host, port=resolved_port)
