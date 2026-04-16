# ABOUTME: Tests for snapshot I/O — writing, reading, listing, and deduplication.
# ABOUTME: Uses a temporary directory; no real filesystem side effects.

import json
import time
from pathlib import Path

import pytest

from apilens.snapshot import list_snapshots, load_snapshot_spec, write_snapshot


@pytest.fixture
def snap_dir(tmp_path):
    return tmp_path / "snapshots"


def test_write_creates_snapshot(snap_dir):
    spec = {"paths": {"/items": {"get": {}}}}
    path = write_snapshot(snap_dir, spec, commit_sha="abc1234", commit_message="initial")
    assert path is not None
    assert path.exists()
    with open(path) as f:
        data = json.load(f)
    assert data["spec"] == spec
    assert data["commit_sha"] == "abc1234"


def test_write_skips_if_unchanged(snap_dir):
    spec = {"paths": {"/items": {"get": {}}}}
    write_snapshot(snap_dir, spec, commit_sha="abc1234", commit_message="first")
    second = write_snapshot(snap_dir, spec, commit_sha="def5678", commit_message="second")
    assert second is None
    assert len(list(snap_dir.glob("*.json"))) == 1


def test_write_creates_new_if_changed(snap_dir):
    spec_a = {"paths": {"/items": {"get": {}}}}
    spec_b = {"paths": {"/items": {"get": {}}, "/users": {"get": {}}}}
    write_snapshot(snap_dir, spec_a, commit_sha="aaa", commit_message="a")
    time.sleep(0.01)  # ensure different filename timestamp
    path = write_snapshot(snap_dir, spec_b, commit_sha="bbb", commit_message="b")
    assert path is not None
    assert len(list(snap_dir.glob("*.json"))) == 2


def test_list_snapshots_sorted_newest_first(snap_dir):
    spec_a = {"paths": {"/a": {}}}
    spec_b = {"paths": {"/b": {}}}
    write_snapshot(snap_dir, spec_a, commit_sha="aaa", commit_message="a")
    time.sleep(0.01)
    write_snapshot(snap_dir, spec_b, commit_sha="bbb", commit_message="b")
    snapshots = list_snapshots(snap_dir)
    assert len(snapshots) == 2
    assert snapshots[0].commit_sha == "bbb"
    assert snapshots[1].commit_sha == "aaa"


def test_load_snapshot_spec(snap_dir):
    spec = {"paths": {"/items": {}}}
    path = write_snapshot(snap_dir, spec, commit_sha="abc", commit_message="msg")
    loaded = load_snapshot_spec(snap_dir, path.name)
    assert loaded == spec


def test_load_snapshot_spec_not_found(snap_dir):
    snap_dir.mkdir()
    result = load_snapshot_spec(snap_dir, "nonexistent.json")
    assert result is None


def test_load_snapshot_spec_path_traversal(snap_dir):
    snap_dir.mkdir()
    result = load_snapshot_spec(snap_dir, "../../../etc/passwd")
    assert result is None
