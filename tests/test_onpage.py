"""Tests for onpage_analyzer provider."""

import respx
import httpx
import pytest
from pathlib import Path

from advanced_seo_mcp.providers.onpage_analyzer import OnPageAnalyzer
from advanced_seo_mcp.http_client import SafeHTTPClient
from advanced_seo_mcp.models.onpage import OnPageResult


@pytest.fixture
def http_client() -> SafeHTTPClient:
    return SafeHTTPClient(max_retries=1)


@pytest.fixture
def analyzer(http_client: SafeHTTPClient) -> OnPageAnalyzer:
    return OnPageAnalyzer(http_client)


@respx.mock
@pytest.mark.anyio
async def test_onpage_analysis(analyzer: OnPageAnalyzer, fixtures_dir: Path):
    html = (fixtures_dir / "onpage_sample.html").read_text()
    respx.get("https://example.com/test").mock(
        return_value=httpx.Response(200, text=html)
    )

    result = await analyzer.analyze("https://example.com/test")

    assert isinstance(result, OnPageResult)
    assert result.meta_title == "SEO Optimized Test Page"
    assert result.meta_title_length == 23
    assert (
        result.meta_description
        == "This is a test page with proper SEO meta tags for analysis"
    )
    assert result.meta_description_length == 58
    assert result.h1_count == 1
    assert result.h1_tags == ["Main Heading"]
    assert result.h2_count == 2
    assert result.word_count > 300
    assert result.thin_content is False
    assert result.internal_links >= 1
    assert result.external_links >= 1
    assert result.total_images == 2
    assert result.images_missing_alt == 1


@respx.mock
@pytest.mark.anyio
async def test_onpage_fetch_error(http_client: SafeHTTPClient):
    analyzer = OnPageAnalyzer(http_client)
    respx.get("https://broken.com/page").mock(return_value=httpx.Response(500))
    result = await analyzer.analyze("https://broken.com/page")
    assert "error" in result
    assert result["error"]["code"] == "fetch_failed"
