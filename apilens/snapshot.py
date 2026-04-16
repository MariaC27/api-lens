# ABOUTME: Snapshot I/O — reading, writing, and listing versioned OpenAPI spec files.
# ABOUTME: Each snapshot is a JSON file with timestamp, commit SHA, and the full spec.

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from apilens.models import OpenAPISpec, SnapshotMeta

logger = logging.getLogger(__name__)


def list_snapshots(snapshots_dir: Path) -> list[SnapshotMeta]:
    """Return snapshot metadata sorted newest first."""
    snapshots = []
    for path in sorted(snapshots_dir.glob("*.json"), reverse=True):
        try:
            with open(path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.warning("Skipping corrupt snapshot %s: %s", path.name, e)
            continue
        snapshots.append(
            SnapshotMeta(
                filename=path.name,
                timestamp=data.get("timestamp", ""),
                commit_sha=data.get("commit_sha", ""),
                commit_message=data.get("commit_message", ""),
            )
        )
    return snapshots


def load_snapshot_spec(snapshots_dir: Path, filename: str) -> Optional[OpenAPISpec]:
    """Load the OpenAPI spec from a snapshot file. Returns None if not found."""
    path = (snapshots_dir / filename).resolve()
    if not path.is_relative_to(snapshots_dir.resolve()):
        logger.warning("Rejected unsafe snapshot filename: %s", filename)
        return None
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    return data.get("spec")


def write_snapshot(
    snapshots_dir: Path,
    spec: OpenAPISpec,
    commit_sha: str,
    commit_message: str,
) -> Optional[Path]:
    """Write a new snapshot if the spec has changed since the last one.

    Returns the path of the written snapshot, or None if skipped (no changes).
    """
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    existing = sorted(snapshots_dir.glob("*.json"), reverse=True)
    if existing:
        with open(existing[0]) as f:
            last_spec = json.load(f).get("spec", {})
        if last_spec == spec:
            logger.info("No API changes detected — skipping snapshot.")
            return None

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    short_sha = commit_sha[:7] if commit_sha else "unknown"
    filename = f"{timestamp}_{short_sha}.json"
    path = snapshots_dir / filename

    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "commit_sha": commit_sha,
        "commit_message": commit_message,
        "spec": spec,
    }

    with open(path, "w") as f:
        json.dump(snapshot, f, indent=2)

    logger.info("Snapshot written to %s", path)
    return path
