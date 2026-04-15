"""Schema markup validator provider."""

import json
from typing import Any

from bs4 import BeautifulSoup

from ..http_client import SafeHTTPClient
from ..responses import make_error_response
from .base import BaseProvider


class SchemaValidator(BaseProvider):
    """Extracts and validates JSON-LD Schema Markup from a URL."""

    def __init__(self, http_client: SafeHTTPClient):
        super().__init__(http_client)

    async def analyze(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """Check for JSON-LD schema markup."""
        url = self._normalize_url(url)
        try:
            resp = await self.http.get(url)
        except Exception as exc:
            return make_error_response(
                code="fetch_failed",
                message=str(exc),
                provider="schema",
                retryable=True,
            )

        soup = BeautifulSoup(resp.content, "lxml")
        scripts = soup.find_all("script", type="application/ld+json")
        results = []

        for script in scripts:
            content = script.string or script.text or ""
            try:
                data = json.loads(content)
                results.append(
                    {
                        "valid": True,
                        "type": data.get("@type", "Unknown"),
                        "context": data.get("@context", "Unknown"),
                        "raw": data,
                    }
                )
            except json.JSONDecodeError as exc:
                results.append(
                    {
                        "valid": False,
                        "error": f"JSON Decode Error: {exc}",
                        "content_snippet": content[:50] + "..." if content else "Empty",
                    }
                )

        return {
            "found_count": len(scripts),
            "schemas": results,
            "has_valid_schema": any(s["valid"] for s in results),
        }
