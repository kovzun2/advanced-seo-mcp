"""Sitemap auditor provider."""

import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import urlparse

from ..http_client import SafeHTTPClient
from .base import BaseProvider
from .onpage_analyzer import OnPageAnalyzer


class SitemapAuditor(BaseProvider):
    """Fetches sitemap and runs on-page audit on selected pages."""

    def __init__(self, http_client: SafeHTTPClient):
        super().__init__(http_client)
        self._onpage = OnPageAnalyzer(http_client)

    async def analyze(self, url: str, limit: int = 5, **kwargs: Any) -> dict[str, Any]:
        """Fetch sitemap, audit first N pages."""
        url = self._normalize_url(url)
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        sitemap_urls = await self._fetch_sitemap_urls(base)
        if not sitemap_urls:
            return {"error": "No sitemap found or empty sitemap."}

        selected = sitemap_urls[:limit]
        issues = {"missing_h1": [], "missing_meta_desc": [], "thin_content": []}

        for page_url in selected:
            data = await self._onpage.analyze(page_url)
            if isinstance(data, dict) and "error" in data:
                continue
            if data.h1_count == 0:
                issues["missing_h1"].append(page_url)
            if not data.meta_description:
                issues["missing_meta_desc"].append(page_url)
            if data.thin_content:
                issues["thin_content"].append(page_url)

        return {
            "total_scanned": len(selected),
            "total_in_sitemap": len(sitemap_urls),
            "issues_summary": {k: len(v) for k, v in issues.items()},
            "issue_details": issues,
        }

    async def _fetch_sitemap_urls(self, base: str) -> list[str]:
        """Try common sitemap locations and extract URLs."""
        candidates = ["/sitemap.xml", "/sitemap_index.xml", "/wp-sitemap.xml"]
        content = None

        for path in candidates:
            try:
                resp = await self.http.get(f"{base}{path}")
                content = resp.content
                break
            except Exception:
                continue

        if not content:
            return []

        try:
            root = ET.fromstring(content)
            urls = []
            for child in root:
                for sub in child:
                    if "loc" in sub.tag:
                        if sub.text:
                            urls.append(sub.text)
                if "loc" in child.tag and child.text:
                    urls.append(child.text)
            return list(set(u for u in urls if u))
        except ET.ParseError:
            return []
