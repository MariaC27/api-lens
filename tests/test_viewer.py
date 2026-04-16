# ABOUTME: Tests for the standalone FastAPI viewer app.
# ABOUTME: Covers the HTML endpoint, snapshot listing, and compare endpoints.

import json

import pytest
from fastapi.testclient import TestClient

from apilens.snapshot import write_snapshot
from apilens.viewer.app import _make_app


@pytest.fixture
def snap_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


@pytest.fixture
def client(snap_dir):
    app = _make_app(snapshots_dir=snap_dir)
    return TestClient(app)


def _write(snap_dir, spec, sha="abc1234", msg="test"):
    import time
    time.sleep(0.01)
    return write_snapshot(snap_dir, spec, commit_sha=sha, commit_message=msg)


class TestViewer:
    def test_html_served(self, client):
        res = client.get("/")
        assert res.status_code == 200
        assert "ApiLens" in res.text
        assert "text/html" in res.headers["content-type"]

    def test_snapshots_empty(self, client):
        res = client.get("/snapshots")
        assert res.status_code == 200
        assert res.json() == []

    def test_snapshots_listed(self, client, snap_dir):
        _write(snap_dir, {"paths": {"/a": {}}}, sha="aaa111", msg="first")
        res = client.get("/snapshots")
        data = res.json()
        assert len(data) == 1
        assert data[0]["commit_sha"] == "aaa111"

    def test_compare_returns_diff(self, client, snap_dir):
        spec_a = {"paths": {"/items": {"get": {}}}, "components": {}}
        spec_b = {"paths": {"/items": {"get": {}}, "/users": {"get": {}}}, "components": {}}
        path_a = _write(snap_dir, spec_a, sha="aaa", msg="a")
        path_b = _write(snap_dir, spec_b, sha="bbb", msg="b")
        res = client.get(f"/compare?base={path_a.name}&head={path_b.name}")
        assert res.status_code == 200
        diff = res.json()
        assert len(diff["new_endpoints"]) == 1
        assert diff["new_endpoints"][0]["path"] == "/users"

    def test_compare_missing_snapshot(self, client, snap_dir):
        _write(snap_dir, {"paths": {}}, sha="aaa", msg="a")
        res = client.get("/compare?base=nonexistent.json&head=nonexistent.json")
        assert res.status_code == 404


class TestViewerAuth:
    def test_password_required_when_set(self, snap_dir):
        app = _make_app(snapshots_dir=snap_dir, password="secret")
        client = TestClient(app, raise_server_exceptions=False)
        res = client.get("/")
        assert res.status_code == 401

    def test_correct_password_grants_access(self, snap_dir):
        import base64
        app = _make_app(snapshots_dir=snap_dir, password="secret")
        client = TestClient(app)
        token = base64.b64encode(b"user:secret").decode()
        res = client.get("/", headers={"Authorization": f"Basic {token}"})
        assert res.status_code == 200

    def test_wrong_password_rejected(self, snap_dir):
        import base64
        app = _make_app(snapshots_dir=snap_dir, password="secret")
        client = TestClient(app, raise_server_exceptions=False)
        token = base64.b64encode(b"user:wrong").decode()
        res = client.get("/", headers={"Authorization": f"Basic {token}"})
        assert res.status_code == 401
