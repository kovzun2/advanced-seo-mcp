"""Link inspector — finds broken links on a page."""

import asyncio
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from ..http_client import SafeHTTPClient
from ..responses import make_error_response
from .base import BaseProvider


class LinkInspector(BaseProvider):
    """Scans a page for broken links (4xx/5xx)."""

    def __init__(self, http_client: SafeHTTPClient):
        super().__init__(http_client)

    async def analyze(self, url: str, limit: int = 20, **kwargs: Any) -> dict[str, Any]:
        """Scan page for broken links."""
        url = self._normalize_url(url)
        try:
            resp = await self.http.get(url)
        except Exception as exc:
            return make_error_response(
                code="fetch_failed",
                message=str(exc),
                provider="links",
                retryable=True,
            )

        soup = BeautifulSoup(resp.content, "lxml")
        links = soup.find_all("a", href=True)

        targets: set[str] = set()
        for link in links:
            href = str(link["href"])
            full = urljoin(str(resp.url), href)
            parsed = urlparse(full)
            if parsed.scheme in ("http", "https"):
                targets.add(full)

        target_list = list(targets)[:limit]
        broken = []
        working = []

        async def check(target: str) -> dict[str, Any]:
            try:
                resp = await self.http.get_with_fallback(target)
                return {"url": target, "status": resp.status_code, "status_text": "OK"}
            except Exception as exc:
                status = getattr(exc, "response", None)
                code = status.status_code if status else 0
                return {"url": target, "status": code, "status_text": "Broken"}

        results = await asyncio.gather(*[check(t) for t in target_list])
        for r in results:
            if r["status"] >= 400 or r["status"] == 0:
                broken.append(r)
            else:
                working.append(r)

        return {
            "total_scanned": len(target_list),
            "broken_count": len(broken),
            "broken_links": broken,
            "working_count": len(working),
        }
