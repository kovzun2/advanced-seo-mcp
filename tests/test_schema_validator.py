"""Tests for schema_validator provider."""

import respx
import httpx
import pytest

from advanced_seo_mcp.providers.schema_validator import SchemaValidator
from advanced_seo_mcp.http_client import SafeHTTPClient


@pytest.fixture
def http_client() -> SafeHTTPClient:
    return SafeHTTPClient(max_retries=1)


@pytest.fixture
def validator(http_client: SafeHTTPClient) -> SchemaValidator:
    return SchemaValidator(http_client)


@respx.mock
@pytest.mark.anyio
async def test_valid_schema(validator: SchemaValidator):
    html = '''<html><head>
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"Test"}</script>
    </head><body></body></html>'''
    respx.get("https://example.com/page").mock(return_value=httpx.Response(200, text=html))
    result = await validator.analyze("https://example.com/page")
    assert result["found_count"] == 1
    assert result["has_valid_schema"] is True
    assert result["schemas"][0]["type"] == "Organization"


@respx.mock
@pytest.mark.anyio
async def test_no_schema(validator: SchemaValidator):
    respx.get("https://example.com/no").mock(return_value=httpx.Response(200, text="<html></html>"))
    result = await validator.analyze("https://example.com/no")
    assert result["found_count"] == 0
    assert result["has_valid_schema"] is False
