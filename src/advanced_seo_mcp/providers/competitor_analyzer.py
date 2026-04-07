"""Competitor domain analyzer provider."""

from typing import Any

from ..http_client import SafeHTTPClient
from .base import BaseProvider
from .ahrefs_api import AhrefsClient


class CompetitorAnalyzer(BaseProvider):
    """Compares two domains using Ahrefs API data."""

    def __init__(self, http_client: SafeHTTPClient, ahrefs_client: AhrefsClient):
        super().__init__(http_client)
        self.ahrefs = ahrefs_client

    async def analyze(
        self, url: str, competitor: str = "", **kwargs: Any
    ) -> dict[str, Any]:
        """Compare two domains.

        Args:
            url: First domain (e.g. 'example.com')
            competitor: Second domain (e.g. 'competitor.com')
        """
        domain1 = url.replace("https://", "").replace("http://", "").strip("/")
        domain2 = competitor.replace("https://", "").replace("http://", "").strip("/")

        if not domain2:
            return {"error": "Competitor domain required"}

        d1 = await self.ahrefs.get_backlinks(domain1)
        d2 = await self.ahrefs.get_backlinks(domain2)

        if isinstance(d1, dict) and "error" in d1:
            return d1
        if isinstance(d2, dict) and "error" in d2:
            return d2

        # At this point d1 and d2 are BacklinkData
        assert not isinstance(d1, dict), "Expected BacklinkData"
        assert not isinstance(d2, dict), "Expected BacklinkData"

        return {
            "domains": [domain1, domain2],
            "comparison": {
                "domain_rating": {
                    domain1: d1.domain_rating,
                    domain2: d2.domain_rating,
                    "winner": domain1
                    if d1.domain_rating > d2.domain_rating
                    else domain2,
                },
                "total_backlinks": {
                    domain1: d1.total_backlinks,
                    domain2: d2.total_backlinks,
                    "diff": d1.total_backlinks - d2.total_backlinks,
                },
            },
        }
