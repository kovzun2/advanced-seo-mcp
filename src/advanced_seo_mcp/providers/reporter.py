"""Report orchestrator and markdown formatter."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config import get_settings
from ..http_client import SafeHTTPClient
from ..models.report import SEOReport
from .onpage_analyzer import OnPageAnalyzer
from .technical_auditor import TechnicalAuditor
from .psi_analyzer import PSIAnalyzer
from .schema_validator import SchemaValidator
from .link_inspector import LinkInspector
from .content_analyzer import ContentAnalyzer
from .ahrefs_api import AhrefsClient


class ReportOrchestrator:
    """Runs all providers and assembles an SEOReport."""

    def __init__(self, http_client: SafeHTTPClient):
        self.http = http_client
        self.onpage = OnPageAnalyzer(http_client)
        self.technical = TechnicalAuditor(http_client)
        self.psi = PSIAnalyzer(http_client)
        self.schema = SchemaValidator(http_client)
        self.links = LinkInspector(http_client)
        self.content = ContentAnalyzer(http_client)
        self.ahrefs = AhrefsClient(api_token=get_settings().ahrefs_api_token or "")

    async def run_full_audit(self, url: str, include_ahrefs: bool = True) -> SEOReport:
        """Run comprehensive audit and save Markdown report."""
        url_normalized = OnPageAnalyzer._normalize_url(url)
        domain = url_normalized.replace("https://", "").replace("http://", "").strip("/")

        # Run independent checks in parallel
        onpage, technical = await asyncio.gather(
            self.onpage.analyze(url_normalized),
            self.technical.analyze(url_normalized),
            return_exceptions=True,
        )

        # Handle errors gracefully
        onpage_result = onpage if not isinstance(onpage, Exception) else {"error": str(onpage)}
        tech_result = technical if not isinstance(technical, Exception) else {"error": str(technical)}

        # Score calculation
        score = 50
        if isinstance(onpage_result, dict) and "error" not in onpage_result:
            if onpage_result.meta_title_optimal:
                score += 5
            if onpage_result.meta_description_optimal:
                score += 5
            if not onpage_result.thin_content:
                score += 5
        if isinstance(tech_result, dict) and "error" not in tech_result:
            score += tech_result.score // 10

        score = min(100, max(0, score))

        report = SEOReport(
            generated_at=datetime.now(),
            url=url_normalized,
            domain=domain,
            overall_score=score,
            summary=f"SEO audit for {domain}. Score: {score}/100.",
        )

        # Save Markdown
        formatter = MarkdownFormatter()
        file_path = formatter.save(report, onpage_result, tech_result)

        return report


class MarkdownFormatter:
    """Formats SEOReport as Markdown and saves to file."""

    def save(self, report: SEOReport, onpage: Any, technical: Any) -> Path:
        """Generate and save Markdown report. Returns file path."""
        settings = get_settings()
        settings.reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"seo_report_{report.domain.replace('.', '_')}_{timestamp}.md"
        file_path = settings.reports_dir / filename

        parts = []
        parts.append(f"# SEO Audit Report: {report.domain}")
        parts.append(f"**Date:** {report.generated_at.strftime('%Y-%m-%d %H:%M')}")
        parts.append(f"**URL:** {report.url}")
        parts.append(f"**Overall Score:** {report.overall_score}/100\n")

        if isinstance(onpage, dict) and "error" not in onpage:
            parts.append("## On-Page SEO")
            parts.append(f"- Title: `{onpage.meta_title}` ({onpage.meta_title_length} chars)")
            parts.append(f"- Description: `{onpage.meta_description}` ({onpage.meta_description_length} chars)")
            parts.append(f"- H1 count: {onpage.h1_count}")
            parts.append(f"- Word count: {onpage.word_count}")
            parts.append(f"- Images missing alt: {onpage.images_missing_alt}")
            if onpage.issues:
                parts.append("\n### Issues")
                for issue in onpage.issues:
                    parts.append(f"- [{issue.severity.upper()}] {issue.message}")

        if isinstance(technical, dict) and "error" not in technical:
            parts.append("\n## Technical Health")
            parts.append(f"- robots.txt: {'✅' if technical.has_robots_txt else '❌'}")
            parts.append(f"- Sitemap: {'✅' if technical.has_sitemap else '❌'}")
            parts.append(f"- HTTPS: {'✅' if technical.https_enabled else '❌'}")
            parts.append(f"- HSTS: {'✅' if technical.hsts_enabled else '❌'}")
            parts.append(f"- Score: {technical.score}/100")

        content = "\n".join(parts)
        file_path.write_text(content, encoding="utf-8")
        return file_path
