"""Helpers for consistent public tool responses."""

from typing import Any

from .models.common import ErrorDetails, SEOBaseModel


def make_error_response(
    *,
    code: str,
    message: str,
    provider: str,
    retryable: bool = False,
    details: dict[str, Any] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """Create a normalized error response."""
    payload: dict[str, Any] = {
        "error": ErrorDetails(
            code=code,
            message=message,
            retryable=retryable,
            provider=provider,
            details=details or {},
        ).model_dump()
    }
    payload.update(extra)
    return payload


def normalize_tool_output(
    result: SEOBaseModel | dict[str, Any],
    *,
    tool_name: str,
    provider: str,
    capability: str = "stable",
    requires_api_key: bool = False,
) -> dict[str, Any]:
    """Attach stable metadata to a tool result without hiding original fields."""
    payload = result.model_dump() if isinstance(result, SEOBaseModel) else dict(result)
    has_error = isinstance(payload.get("error"), dict)
    partial = bool(payload.pop("_partial", False))

    payload["_meta"] = {
        "tool": tool_name,
        "provider": provider,
        "status": "error" if has_error else "partial" if partial else "ok",
        "capability": capability,
        "requires_api_key": requires_api_key,
        "partial": partial,
    }
    return payload
