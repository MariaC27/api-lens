# ABOUTME: Core diff logic for comparing two OpenAPI specs at the field level.
# ABOUTME: Pure functions — no I/O, no side effects.

from typing import Any

from apilens.models import (
    DiffResult,
    EndpointChange,
    EndpointEntry,
    FieldEntry,
    FieldStatus,
    ModifiedEndpoint,
    OpenAPISpec,
)


def resolve_ref(ref_path: str, components: dict[str, Any]) -> dict[str, Any]:
    parts = ref_path.lstrip("#/").split("/")
    node: dict[str, Any] = {"components": components}
    for part in parts:
        node = node.get(part, {})
    return node


def resolve_schema(
    schema: dict[str, Any],
    components: dict[str, Any],
    seen: frozenset[str] | None = None,
) -> dict[str, Any]:
    if seen is None:
        seen = frozenset()
    if not isinstance(schema, dict):
        return schema
    if "$ref" in schema:
        ref = schema["$ref"]
        if ref in seen:
            return {}
        return resolve_schema(resolve_ref(ref, components), components, seen | {ref})
    return {k: resolve_schema(v, components, seen) for k, v in schema.items()}


def extract_properties(
    schema: dict[str, Any], components: dict[str, Any]
) -> dict[str, Any]:
    resolved = resolve_schema(schema, components)
    props = dict(resolved.get("properties") or {})
    for sub in resolved.get("allOf") or []:
        props.update(resolve_schema(sub, components).get("properties") or {})
    return props


def build_fields(
    base_props: dict[str, Any], head_props: dict[str, Any]
) -> list[FieldEntry]:
    fields = []
    for name in head_props:
        status = FieldStatus.added if name not in base_props else FieldStatus.unchanged
        fields.append(FieldEntry(name=name, status=status))
    for name in base_props:
        if name not in head_props:
            fields.append(FieldEntry(name=name, status=FieldStatus.removed))
    return fields


def _request_schema(operation: dict[str, Any]) -> dict[str, Any]:
    return (
        operation.get("requestBody", {})
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )


def _response_schema(operation: dict[str, Any], status: str) -> dict[str, Any]:
    return (
        operation.get("responses", {})
        .get(status, {})
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )


def compare_specs(base: OpenAPISpec, head: OpenAPISpec) -> DiffResult:
    base_components = base.get("components", {})
    head_components = head.get("components", {})
    base_paths = base.get("paths", {})
    head_paths = head.get("paths", {})

    new_endpoints = []
    missing_endpoints = []
    modified_endpoints = []

    for path, methods in head_paths.items():
        for method in methods:
            if path not in base_paths or method not in base_paths[path]:
                new_endpoints.append(EndpointEntry(method=method.upper(), path=path))

    for path, methods in base_paths.items():
        for method in methods:
            if path not in head_paths or method not in head_paths[path]:
                missing_endpoints.append(
                    EndpointEntry(method=method.upper(), path=path)
                )

    for path in head_paths:
        if path not in base_paths:
            continue
        for method in head_paths[path]:
            if method not in base_paths[path]:
                continue

            base_op = base_paths[path][method]
            head_op = head_paths[path][method]
            changes = []

            base_req = _request_schema(base_op)
            head_req = _request_schema(head_op)
            if base_req or head_req:
                base_props = extract_properties(base_req, base_components)
                head_props = extract_properties(head_req, head_components)
                fields = build_fields(base_props, head_props)
                if any(f.status != FieldStatus.unchanged for f in fields):
                    changes.append(
                        EndpointChange(location="request body", fields=fields)
                    )

            for status in ("200", "201"):
                base_props = extract_properties(
                    _response_schema(base_op, status), base_components
                )
                head_props = extract_properties(
                    _response_schema(head_op, status), head_components
                )
                fields = build_fields(base_props, head_props)
                if any(f.status != FieldStatus.unchanged for f in fields):
                    changes.append(
                        EndpointChange(location=f"response {status}", fields=fields)
                    )

            if changes:
                modified_endpoints.append(
                    ModifiedEndpoint(method=method.upper(), path=path, changes=changes)
                )

    return DiffResult(
        new_endpoints=new_endpoints,
        missing_endpoints=missing_endpoints,
        modified_endpoints=modified_endpoints,
    )
