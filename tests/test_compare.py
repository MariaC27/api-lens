# ABOUTME: Tests for the core OpenAPI spec comparison logic.
# ABOUTME: Covers added/removed/modified endpoints and field-level diff.

import pytest

from apilens.compare import compare_specs
from apilens.models import FieldStatus


def _spec(paths: dict) -> dict:
    return {"paths": paths, "components": {}}


def _op(response_props: dict | None = None, request_props: dict | None = None) -> dict:
    op: dict = {}
    if response_props is not None:
        op["responses"] = {
            "200": {
                "content": {
                    "application/json": {
                        "schema": {"type": "object", "properties": response_props}
                    }
                }
            }
        }
    if request_props is not None:
        op["requestBody"] = {
            "content": {
                "application/json": {
                    "schema": {"type": "object", "properties": request_props}
                }
            }
        }
    return op


class TestNewAndMissingEndpoints:
    def test_new_endpoint_detected(self):
        base = _spec({"/items": {"get": _op()}})
        head = _spec({"/items": {"get": _op()}, "/users": {"get": _op()}})
        diff = compare_specs(base, head)
        assert len(diff.new_endpoints) == 1
        assert diff.new_endpoints[0].path == "/users"
        assert diff.new_endpoints[0].method == "GET"

    def test_removed_endpoint_detected(self):
        base = _spec({"/items": {"get": _op()}, "/users": {"get": _op()}})
        head = _spec({"/items": {"get": _op()}})
        diff = compare_specs(base, head)
        assert len(diff.missing_endpoints) == 1
        assert diff.missing_endpoints[0].path == "/users"

    def test_no_changes(self):
        spec = _spec({"/items": {"get": _op(response_props={"id": {}, "name": {}})}})
        diff = compare_specs(spec, spec)
        assert diff.new_endpoints == []
        assert diff.missing_endpoints == []
        assert diff.modified_endpoints == []


class TestModifiedEndpoints:
    def test_added_response_field(self):
        base = _spec({"/items": {"get": _op(response_props={"id": {}})}})
        head = _spec({"/items": {"get": _op(response_props={"id": {}, "name": {}})}})
        diff = compare_specs(base, head)
        assert len(diff.modified_endpoints) == 1
        ep = diff.modified_endpoints[0]
        assert ep.path == "/items"
        assert ep.method == "GET"
        fields = {f.name: f.status for f in ep.changes[0].fields}
        assert fields["name"] == FieldStatus.added
        assert fields["id"] == FieldStatus.unchanged

    def test_removed_response_field(self):
        base = _spec({"/items": {"get": _op(response_props={"id": {}, "name": {}})}})
        head = _spec({"/items": {"get": _op(response_props={"id": {}})}})
        diff = compare_specs(base, head)
        assert len(diff.modified_endpoints) == 1
        fields = {f.name: f.status for f in diff.modified_endpoints[0].changes[0].fields}
        assert fields["name"] == FieldStatus.removed

    def test_added_request_field(self):
        base = _spec({"/items": {"post": _op(request_props={"name": {}})}})
        head = _spec({"/items": {"post": _op(request_props={"name": {}, "price": {}})}})
        diff = compare_specs(base, head)
        assert len(diff.modified_endpoints) == 1
        change = diff.modified_endpoints[0].changes[0]
        assert change.location == "request body"
        fields = {f.name: f.status for f in change.fields}
        assert fields["price"] == FieldStatus.added

    def test_unchanged_fields_not_in_modified(self):
        spec = _spec({"/items": {"get": _op(response_props={"id": {}, "name": {}})}})
        diff = compare_specs(spec, spec)
        assert diff.modified_endpoints == []
