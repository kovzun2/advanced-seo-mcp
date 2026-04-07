"""Advanced SEO MCP Server — MCP tools for AI agents."""

import asyncio
import logging
from pathlib import Path
from typing import Annotated, Any

from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import Field

# Load env vars before anything else
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from .config import get_settings
from .http_client import SafeHTTPClient, RateLimiter
from .providers.onpage_analyzer import OnPageAnalyzer
from .providers.technical_auditor import TechnicalAuditor
from .providers.psi_analyzer import PSIAnalyzer
from .providers.schema_validator import SchemaValidator
from .providers.link_inspector import LinkInspector
from .providers.content_analyzer import ContentAnalyzer
from .providers.sitemap_auditor import SitemapAuditor
from .providers.competitor_analyzer import CompetitorAnalyzer
from .providers.ahrefs_api import AhrefsClient
from .providers.reporter import ReportOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("Advanced SEO MCP")


def _make_http_client() -> SafeHTTPClient:
    settings = get_settings()
    return SafeHTTPClient(
        timeout=settings.http_timeout,
        max_retries=settings.http_max_retries,
        rate_limiter=RateLimiter(settings.rate_limit_per_second),
    )


@mcp.tool()
def generate_audit_report(
    url: Annotated[str, Field(description="URL to audit", min_length=3)],
    include_ahrefs: Annotated[bool, Field(description="Include Ahrefs data")] = True,
) -> str:
    """Generates a full SEO audit report (Markdown) and saves it locally."""
    client = _make_http_client()
    orchestrator = ReportOrchestrator(client)
    report = asyncio.run(orchestrator.run_full_audit(url, include_ahrefs))
    return f"Report saved: {report.domain} — check reports/ directory"


@mcp.tool()
def analyze_page_speed(
    url: Annotated[str, Field(description="URL to analyze", min_length=3)],
    strategy: Annotated[str, Field(description="mobile or desktop")] = "mobile",
) -> dict[str, Any]:
    """Analyzes site speed using Google PageSpeed Insights."""
    client = _make_http_client()
    psi = PSIAnalyzer(client)
    result = asyncio.run(psi.analyze(url, strategy))
    return result if isinstance(result, dict) else result.model_dump()


@mcp.tool()
def check_schema_markup(
    url: Annotated[str, Field(description="URL to check", min_length=3)],
) -> dict[str, Any]:
    """Validates JSON-LD Schema Markup on a page."""
    client = _make_http_client()
    validator = SchemaValidator(client)
    return asyncio.run(validator.analyze(url))


@mcp.tool()
def check_broken_links_on_page(
    url: Annotated[str, Field(description="URL to scan", min_length=3)],
    limit: Annotated[int, Field(description="Max links to check", ge=1, le=50)] = 20,
) -> dict[str, Any]:
    """Scans a page for broken links (404s)."""
    client = _make_http_client()
    inspector = LinkInspector(client)
    return asyncio.run(inspector.analyze(url, limit=limit))


@mcp.tool()
def analyze_content_density(
    url: Annotated[str, Field(description="URL to analyze", min_length=3)],
    target_keyword: Annotated[str | None, Field(description="Target keyword")] = None,
) -> dict[str, Any]:
    """Analyzes keyword density and TF-IDF metrics."""
    client = _make_http_client()
    analyzer = ContentAnalyzer(client)
    return asyncio.run(analyzer.analyze(url, target_keyword=target_keyword))


@mcp.tool()
def compare_competitors(
    my_domain: Annotated[str, Field(description="Your domain", min_length=3)],
    competitor_domain: Annotated[str, Field(description="Competitor domain", min_length=3)],
) -> dict[str, Any]:
    """Compares SEO metrics of two domains."""
    client = _make_http_client()
    ahrefs = AhrefsClient(api_token=get_settings().ahrefs_api_token or "")
    competitor = CompetitorAnalyzer(client, ahrefs)
    return asyncio.run(competitor.analyze(my_domain, competitor=competitor_domain))


@mcp.tool()
def bulk_sitemap_audit(
    url: Annotated[str, Field(description="Domain URL", min_length=3)],
    limit: Annotated[int, Field(description="Max pages to scan", ge=1, le=50)] = 5,
) -> dict[str, Any]:
    """Scans the sitemap and runs On-Page audit on multiple pages."""
    client = _make_http_client()
    auditor = SitemapAuditor(client)
    return asyncio.run(auditor.analyze(url, limit=limit))


@mcp.tool()
def onpage_audit(
    url: Annotated[str, Field(description="URL to audit", min_length=3)],
) -> dict[str, Any]:
    """Performs a detailed on-page SEO audit."""
    client = _make_http_client()
    analyzer = OnPageAnalyzer(client)
    result = asyncio.run(analyzer.analyze(url))
    return result if isinstance(result, dict) else result.model_dump()


@mcp.tool()
def technical_health_check(
    url: Annotated[str, Field(description="Domain or URL to check", min_length=3)],
) -> dict[str, Any]:
    """Checks technical SEO aspects of a domain/URL."""
    client = _make_http_client()
    auditor = TechnicalAuditor(client)
    result = asyncio.run(auditor.analyze(url))
    return result if isinstance(result, dict) else result.model_dump()


@mcp.tool()
def get_backlinks(
    domain: Annotated[str, Field(description="Domain to analyse", min_length=3)],
) -> dict[str, Any]:
    """Retrieves backlink data via Ahrefs API."""
    ahrefs = AhrefsClient(api_token=get_settings().ahrefs_api_token or "")
    result = asyncio.run(ahrefs.get_backlinks(domain))
    return result if isinstance(result, dict) else result.model_dump()


@mcp.tool()
def estimate_traffic(
    domain: Annotated[str, Field(description="Domain to check", min_length=3)],
    country: Annotated[str, Field(description="Country code")] = "None",
) -> dict[str, Any]:
    """Estimates monthly search traffic for a domain."""
    ahrefs = AhrefsClient(api_token=get_settings().ahrefs_api_token or "")
    return asyncio.run(ahrefs.get_traffic(domain, country))


@mcp.tool()
def check_difficulty(
    keyword: Annotated[str, Field(description="Keyword to analyse", min_length=1)],
    country: Annotated[str, Field(description="Country code")] = "us",
) -> dict[str, Any]:
    """Checks keyword difficulty score."""
    ahrefs = AhrefsClient(api_token=get_settings().ahrefs_api_token or "")
    return asyncio.run(ahrefs.get_keyword_difficulty(keyword, country))


def main():
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")


if __name__ == "__main__":
    main()
