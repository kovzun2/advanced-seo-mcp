"""Tests for reporter module."""

from advanced_seo_mcp.providers.reporter import MarkdownFormatter
from advanced_seo_mcp.models.report import SEOReport
from advanced_seo_mcp.models.onpage import OnPageResult
from advanced_seo_mcp.models.technical import TechnicalAudit
from datetime import datetime
import advanced_seo_mcp.config as config_module


def test_markdown_formatter_creates_report(tmp_path):
    # Override reports_dir for test
    config_module._settings = None

    report = SEOReport(
        generated_at=datetime.now(),
        url="https://example.com",
        domain="example.com",
        overall_score=70,
        summary="Test report",
    )
    onpage = OnPageResult(
        url="https://example.com",
        status_code=200,
        response_time_ms=100.0,
        meta_title="Test",
        meta_title_length=4,
        meta_title_optimal=False,
        meta_description="Desc",
        meta_description_length=4,
        meta_description_optimal=False,
        h1_count=1,
        h2_count=0,
        word_count=200,
        thin_content=False,
        total_links=0,
        internal_links=0,
        external_links=0,
        total_images=0,
        images_missing_alt=0,
    )
    tech = TechnicalAudit(
        domain="example.com",
        has_robots_txt=True,
        has_sitemap=True,
        https_enabled=True,
        hsts_enabled=True,
        score=80,
    )

    formatter = MarkdownFormatter()
    import os

    os.chdir(tmp_path)
    path = formatter.save(report, onpage, tech)
    assert path.exists()
    content = path.read_text()
    assert "# SEO Audit Report: example.com" in content
    assert "**Overall Score:** 70/100" in content
