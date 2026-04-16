# ABOUTME: Pydantic models for snapshot metadata and diff results.
# ABOUTME: Used by compare, snapshot, and viewer modules.

from enum import Enum
from typing import Any

from pydantic import BaseModel

# Type alias for an OpenAPI spec document — freeform JSON.
OpenAPISpec = dict[str, Any]


class SnapshotMeta(BaseModel):
    filename: str
    timestamp: str
    commit_sha: str
    commit_message: str


class FieldStatus(str, Enum):
    added = "added"
    removed = "removed"
    unchanged = "unchanged"


class FieldEntry(BaseModel):
    name: str
    status: FieldStatus


class EndpointChange(BaseModel):
    location: str
    fields: list[FieldEntry]


class EndpointEntry(BaseModel):
    method: str
    path: str


class ModifiedEndpoint(BaseModel):
    method: str
    path: str
    changes: list[EndpointChange]


class DiffResult(BaseModel):
    new_endpoints: list[EndpointEntry]
    missing_endpoints: list[EndpointEntry]
    modified_endpoints: list[ModifiedEndpoint]
