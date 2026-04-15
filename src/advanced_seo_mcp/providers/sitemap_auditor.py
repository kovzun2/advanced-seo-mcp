"""Sitemap auditor provider."""

import asyncio
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import urlparse

from ..http_client import SafeHTTPClient
from ..responses import make_error_response
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
            return make_error_response(
                code="sitemap_missing",
                message="No sitemap found or empty sitemap.",
                provider="sitemap",
            )

        selected = sitemap_urls[:limit]
        issues: dict[str, list[str]] = {
            "missing_h1": [],
            "missing_meta_desc": [],
            "thin_content": [],
        }
        failed_pages: list[str] = []

        results = await asyncio.gather(
            *[self._onpage.analyze(page_url) for page_url in selected]
        )
        for page_url, data in zip(selected, results):
            if isinstance(data, dict) and "error" in data:
                failed_pages.append(page_url)
                continue
            if isinstance(data, dict):
                failed_pages.append(page_url)
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
            "failed_pages": failed_pages,
            "_partial": bool(failed_pages),
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
            return await self._extract_urls(root, base)
        except ET.ParseError:
            return []

    async def _extract_urls(
        self, root: ET.Element, base: str, depth: int = 0
    ) -> list[str]:
        if depth > 1:
            return []

        tag = self._strip_namespace(root.tag)
        if tag == "urlset":
            return self._extract_loc_values(root)

        if tag == "sitemapindex":
            nested_urls: list[str] = []
            for sitemap_url in self._extract_loc_values(root):
                if not sitemap_url.startswith(base):
                    continue
                try:
                    resp = await self.http.get(sitemap_url)
                    nested_root = ET.fromstring(resp.content)
                except Exception:
                    continue
                nested_urls.extend(await self._extract_urls(nested_root, base, depth + 1))
            return list(dict.fromkeys(nested_urls))

        return self._extract_loc_values(root)

    @staticmethod
    def _extract_loc_values(root: ET.Element) -> list[str]:
        values: list[str] = []
        for element in root.iter():
            if SitemapAuditor._strip_namespace(element.tag) == "loc" and element.text:
                values.append(element.text.strip())
        return list(dict.fromkeys(values))

    @staticmethod
    def _strip_namespace(tag: str) -> str:
        return tag.split("}", 1)[-1]
