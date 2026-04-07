"""Tests for Pydantic model validation."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from advanced_seo_mcp.models.onpage import OnPageResult
from advanced_seo_mcp.models.technical import TechnicalAudit
from advanced_seo_mcp.models.psi import PageSpeedResult
from advanced_seo_mcp.models.report import SEOReport
from advanced_seo_mcp.models.common import Issue
from advanced_seo_mcp.models.ahrefs import BacklinkEntry, BacklinkData


def test_onpage_result_valid():
    result = OnPageResult(
        url="https://example.com",
        status_code=200,
        response_time_ms=150.0,
        meta_title="Test Page",
        meta_title_length=9,
        meta_title_optimal=False,
        meta_description="A test page",
        meta_description_length=11,
        meta_description_optimal=False,
        h1_count=1,
        h1_tags=["Test"],
        h2_count=2,
        h2_tags=["Section 1", "Section 2"],
        word_count=500,
        thin_content=False,
        total_links=10,
        internal_links=7,
        external_links=3,
        total_images=5,
        images_missing_alt=1,
    )
    assert result.url == "https://example.com"
    assert result.word_count == 500


def test_onpage_rejects_extra_fields():
    with pytest.raises(ValidationError):
        OnPageResult(
            url="https://example.com",
            status_code=200,
            response_time_ms=100.0,
            meta_title="Test",
            meta_title_length=4,
            meta_title_optimal=False,
            meta_description=None,
            meta_description_length=0,
            meta_description_optimal=False,
            h1_count=0,
            h2_count=0,
            word_count=100,
            thin_content=False,
            total_links=0,
            internal_links=0,
            external_links=0,
            total_images=0,
            images_missing_alt=0,
            extra_field="should fail",
        )


def test_technical_audit_valid():
    audit = TechnicalAudit(
        domain="example.com",
        has_robots_txt=True,
        has_sitemap=True,
        https_enabled=True,
        hsts_enabled=True,
        score=85,
    )
    assert audit.score == 85


def test_technical_audit_score_range():
    with pytest.raises(ValidationError):
        TechnicalAudit(
            domain="x.com", has_robots_txt=True, has_sitemap=True,
            https_enabled=True, hsts_enabled=True, score=101
        )


def test_page_speed_strategy_validation():
    with pytest.raises(ValidationError):
        PageSpeedResult(
            strategy="tablet", performance_score=50, seo_score=50,
            lcp="2s", fcp="1s", cls="0.1", inp="100ms"
        )


def test_issue_severity_validation():
    # Valid severities should work
    Issue(message="Test", severity="critical")
    Issue(message="Test", severity="warning")
    Issue(message="Test", severity="info")
    
    # Invalid should fail
    with pytest.raises(ValidationError):
        Issue(message="Test", severity="high")


def test_report_with_all_sections():
    report = SEOReport(
        generated_at=datetime.now(),
        url="https://example.com",
        domain="example.com",
        onpage=OnPageResult(
            url="https://example.com", status_code=200, response_time_ms=100.0,
            meta_title="Test", meta_title_length=4, meta_title_optimal=False,
            meta_description=None, meta_description_length=0, meta_description_optimal=False,
            h1_count=1, h2_count=0, word_count=200, thin_content=False,
            total_links=0, internal_links=0, external_links=0,
            total_images=0, images_missing_alt=0,
        ),
        technical=TechnicalAudit(
            domain="example.com", has_robots_txt=True, has_sitemap=True,
            https_enabled=True, hsts_enabled=True, score=80,
        ),
        overall_score=75,
        summary="Good overall, needs meta improvements.",
    )
    assert report.onpage is not None
    assert report.technical is not None


def test_report_overall_score_range():
    with pytest.raises(ValidationError):
        SEOReport(
            generated_at=datetime.now(), url="https://x.com", domain="x.com",
            overall_score=101, summary="test"
        )
    with pytest.raises(ValidationError):
        SEOReport(
            generated_at=datetime.now(), url="https://x.com", domain="x.com",
            overall_score=-1, summary="test"
        )


def test_backlink_entry_valid():
    entry = BacklinkEntry(
        anchor="test link",
        domain_rating=50,
        url_from="https://referrer.com/page",
        url_to="https://example.com/",
        title="Referring Page",
    )
    assert entry.domain_rating == 50


def test_backlink_entry_domain_rating_range():
    with pytest.raises(ValidationError):
        BacklinkEntry(
            anchor="x", domain_rating=101,
            url_from="http://a.com", url_to="http://b.com"
        )
    with pytest.raises(ValidationError):
        BacklinkEntry(
            anchor="x", domain_rating=-1,
            url_from="http://a.com", url_to="http://b.com"
        )


def test_backlink_data_valid():
    data = BacklinkData(
        domain="example.com",
        domain_rating=50,
        total_backlinks=1000,
        referring_domains=200,
    )
    assert data.domain == "example.com"
    assert data.total_backlinks == 1000


def test_page_speed_score_boundaries():
    with pytest.raises(ValidationError):
        PageSpeedResult(
            strategy="mobile", performance_score=101, seo_score=50,
            lcp="2s", fcp="1s", cls="0.1", inp="100ms"
        )
    with pytest.raises(ValidationError):
        PageSpeedResult(
            strategy="mobile", performance_score=-1, seo_score=50,
            lcp="2s", fcp="1s", cls="0.1", inp="100ms"
        )
