"""Report orchestrator and markdown formatter."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config import get_settings
from ..http_client import SafeHTTPClient
from ..models.onpage import OnPageResult
from ..models.report import SEOReport
from ..models.technical import TechnicalAudit
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
        domain = (
            url_normalized.replace("https://", "").replace("http://", "").strip("/")
        )

        tasks = [
            self.onpage.analyze(url_normalized),
            self.technical.analyze(url_normalized),
            self.schema.analyze(url_normalized),
            self.links.analyze(url_normalized),
            self.content.analyze(url_normalized),
            self.psi.analyze(url_normalized),
        ]
        if include_ahrefs:
            tasks.append(self.ahrefs.get_backlinks(domain))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        onpage_result = self._coerce_result(results[0])
        tech_result = self._coerce_result(results[1])
        schema_result = self._coerce_result(results[2])
        links_result = self._coerce_result(results[3])
        content_result = self._coerce_result(results[4])
        psi_result = self._coerce_result(results[5])
        backlinks_result = self._coerce_result(results[6]) if include_ahrefs else None

        score = 50
        if isinstance(onpage_result, OnPageResult):
            if onpage_result.meta_title_optimal:
                score += 5
            if onpage_result.meta_description_optimal:
                score += 5
            if not onpage_result.thin_content:
                score += 5
        if isinstance(tech_result, TechnicalAudit):
            score += tech_result.score // 10

        score = min(100, max(0, score))

        completed_checks = []
        skipped_checks = []
        sections = {
            "schema": schema_result,
            "links": links_result,
            "content": content_result,
        }

        for name, value in [
            ("onpage", onpage_result),
            ("technical", tech_result),
            ("schema", schema_result),
            ("links", links_result),
            ("content", content_result),
            ("page_speed", psi_result),
            ("backlinks", backlinks_result),
        ]:
            if value is None:
                skipped_checks.append(name)
            elif isinstance(value, dict) and "error" in value:
                skipped_checks.append(name)
            else:
                completed_checks.append(name)

        report = SEOReport(
            generated_at=datetime.now(),
            url=url_normalized,
            domain=domain,
            onpage=onpage_result if isinstance(onpage_result, OnPageResult) else None,
            technical=tech_result if isinstance(tech_result, TechnicalAudit) else None,
            page_speed=psi_result if hasattr(psi_result, "strategy") else None,
            backlinks=backlinks_result if hasattr(backlinks_result, "domain") else None,
            supplemental_sections=sections,
            completed_checks=completed_checks,
            skipped_checks=skipped_checks,
            partial=bool(skipped_checks),
            overall_score=score,
            summary=f"SEO audit for {domain}. Score: {score}/100.",
        )

        formatter = MarkdownFormatter()
        file_path = formatter.save(
            report,
            onpage_result=onpage_result,
            technical_result=tech_result,
            psi_result=psi_result,
            backlinks_result=backlinks_result,
        )
        report = report.model_copy(update={"report_path": str(file_path)})

        return report

    @staticmethod
    def _coerce_result(result: Any) -> Any:
        if isinstance(result, Exception):
            return {"error": {"code": "audit_failed", "message": str(result)}}
        return result


class MarkdownFormatter:
    """Formats SEOReport as Markdown and saves to file."""

    def save(
        self,
        report: SEOReport,
        onpage_result: Any,
        technical_result: Any,
        psi_result: Any | None = None,
        backlinks_result: Any | None = None,
    ) -> Path:
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

        parts.append("")
        parts.append("## Run Status")
        parts.append(
            f"- Completed checks: {', '.join(report.completed_checks) or 'None'}"
        )
        parts.append(
            f"- Skipped/partial checks: {', '.join(report.skipped_checks) or 'None'}"
        )

        if isinstance(onpage_result, OnPageResult):
            parts.append("## On-Page SEO")
            parts.append(
                f"- Title: `{onpage_result.meta_title}` ({onpage_result.meta_title_length} chars)"
            )
            parts.append(
                f"- Description: `{onpage_result.meta_description}` ({onpage_result.meta_description_length} chars)"
            )
            parts.append(f"- H1 count: {onpage_result.h1_count}")
            parts.append(f"- Word count: {onpage_result.word_count}")
            parts.append(f"- Images missing alt: {onpage_result.images_missing_alt}")
            if onpage_result.issues:
                parts.append("\n### Issues")
                for issue in onpage_result.issues:
                    parts.append(f"- [{issue.severity.upper()}] {issue.message}")
        else:
            parts.extend(self._error_section("On-Page SEO", onpage_result))

        if isinstance(technical_result, TechnicalAudit):
            parts.append("\n## Technical Health")
            parts.append(
                f"- robots.txt: {'✅' if technical_result.has_robots_txt else '❌'}"
            )
            parts.append(f"- Sitemap: {'✅' if technical_result.has_sitemap else '❌'}")
            parts.append(
                f"- HTTPS: {'✅' if technical_result.https_enabled else '❌'}"
            )
            parts.append(f"- HSTS: {'✅' if technical_result.hsts_enabled else '❌'}")
            parts.append(f"- Score: {technical_result.score}/100")
        else:
            parts.extend(self._error_section("Technical Health", technical_result))

        parts.extend(
            self._dict_section(
                "Schema Markup",
                report.supplemental_sections.get("schema"),
            )
        )
        parts.extend(
            self._dict_section(
                "Broken Links",
                report.supplemental_sections.get("links"),
            )
        )
        parts.extend(
            self._dict_section(
                "Content Analysis",
                report.supplemental_sections.get("content"),
            )
        )
        parts.extend(self._model_or_error_section("PageSpeed Insights", psi_result))
        parts.extend(self._model_or_error_section("Backlinks", backlinks_result))

        content = "\n".join(parts)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    @staticmethod
    def _error_section(title: str, payload: Any) -> list[str]:
        if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
            return [
                f"\n## {title}",
                f"- Status: skipped",
                f"- Reason: {payload['error'].get('message', 'Unknown error')}",
            ]
        return []

    def _dict_section(self, title: str, payload: Any) -> list[str]:
        if payload is None:
            return []
        if isinstance(payload, dict) and "error" in payload:
            return self._error_section(title, payload)

        lines = [f"\n## {title}"]
        if isinstance(payload, dict):
            for key, value in payload.items():
                if key == "schemas":
                    lines.append(f"- schemas: {len(value)} items")
                elif isinstance(value, list):
                    lines.append(f"- {key}: {len(value)} items")
                else:
                    lines.append(f"- {key}: {value}")
        return lines

    def _model_or_error_section(self, title: str, payload: Any) -> list[str]:
        if payload is None:
            return []
        if isinstance(payload, dict) and "error" in payload:
            return self._error_section(title, payload)
        if hasattr(payload, "model_dump"):
            lines = [f"\n## {title}"]
            for key, value in payload.model_dump().items():
                if isinstance(value, list):
                    lines.append(f"- {key}: {len(value)} items")
                else:
                    lines.append(f"- {key}: {value}")
            return lines
        return []
