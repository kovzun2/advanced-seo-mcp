"""Tests for Ahrefs API client."""

import json

import respx
import httpx
import pytest

from advanced_seo_mcp.providers.ahrefs_api import AhrefsClient
from advanced_seo_mcp.models.ahrefs import BacklinkData


@pytest.fixture
def ahrefs_client() -> AhrefsClient:
    return AhrefsClient(api_token="test-token")


@respx.mock
@pytest.mark.anyio
async def test_get_backlinks(ahrefs_client: AhrefsClient, fixtures_dir):
    response_data = json.loads((fixtures_dir / "ahrefs_backlinks.json").read_text())
    respx.get("https://apiv2.ahrefs.com").mock(
        return_value=httpx.Response(200, json=response_data)
    )

    result = await ahrefs_client.get_backlinks("example.com")
    assert isinstance(result, BacklinkData)
    assert result.domain == "example.com"
    assert result.domain_rating == 50
    assert result.total_backlinks == 1000


@respx.mock
@pytest.mark.anyio
async def test_get_backlinks_no_token():
    client = AhrefsClient(api_token="")
    result = await client.get_backlinks("example.com")
    assert "error" in result
