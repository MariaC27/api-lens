# ABOUTME: Standalone FastAPI app serving the diff viewer and API endpoints.
# ABOUTME: Launched by `apilens serve`; requires no integration into the user's app.

import secrets
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from apilens import snapshot as snapshot_io
from apilens.models import DiffResult, SnapshotMeta
from apilens.compare import compare_specs
from apilens.viewer.ui import VIEWER_HTML

_security = HTTPBasic(auto_error=False)


def _make_app(snapshots_dir: Path, password: Optional[str] = None) -> FastAPI:
    app = FastAPI(title="ApiLens", docs_url=None, redoc_url=None)

    def _auth(credentials: Optional[HTTPBasicCredentials] = Depends(_security)) -> None:
        if password is None:
            return
        if credentials is None or not secrets.compare_digest(
            credentials.password.encode(), password.encode()
        ):
            raise HTTPException(
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="ApiLens"'},
            )

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def viewer(_: None = Depends(_auth)):
        return VIEWER_HTML

    @app.get("/snapshots", response_model=list[SnapshotMeta])
    def list_snapshots(_: None = Depends(_auth)):
        return snapshot_io.list_snapshots(snapshots_dir)

    @app.get("/compare", response_model=DiffResult)
    def compare(base: str, head: str, _: None = Depends(_auth)):
        base_spec = snapshot_io.load_snapshot_spec(snapshots_dir, base)
        if base_spec is None:
            raise HTTPException(status_code=404, detail=f"Snapshot not found: {base}")
        head_spec = snapshot_io.load_snapshot_spec(snapshots_dir, head)
        if head_spec is None:
            raise HTTPException(status_code=404, detail=f"Snapshot not found: {head}")
        return compare_specs(base_spec, head_spec)

    return app


def mount(app: FastAPI, path: str = "/apilens", password: Optional[str] = None, snapshots_dir: Optional[Path] = None) -> None:
    """Mount the ApiLens viewer onto an existing FastAPI app.

    Example:
        import os
        from apilens.viewer.app import mount
        mount(app, path="/apilens", password=os.environ.get("APILENS_PASSWORD"))
    """
    from apilens.config import load

    conf = load()
    resolved_dir = snapshots_dir or conf.snapshots_dir
    viewer = _make_app(snapshots_dir=resolved_dir, password=password)
    app.mount(path, viewer)
