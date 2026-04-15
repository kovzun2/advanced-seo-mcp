"""Official Ahrefs API v2 client."""

import logging
from typing import Any

import httpx

from ..models.ahrefs import BacklinkData, BacklinkEntry
from ..responses import make_error_response

logger = logging.getLogger(__name__)

AHREFS_API_URL = "https://apiv2.ahrefs.com"


class AhrefsClient:
    """Client for the official Ahrefs API v2."""

    def __init__(self, api_token: str):
        self.api_token = api_token

    async def get_backlinks(
        self, domain: str, limit: int = 10
    ) -> BacklinkData | dict[str, str]:
        """Get backlink overview and top backlinks for a domain."""
        if not self.api_token:
            return make_error_response(
                code="missing_api_key",
                message="AHREFS_API_TOKEN not configured — sign up at https://ahrefs.com/api",
                provider="ahrefs",
                details={"env_var": "AHREFS_API_TOKEN"},
            )

        params = {
            "from": "backlinks",
            "target": domain,
            "mode": "subdomains",
            "limit": str(limit),
            "order_by": "domain_rating:desc",
            "output": "json",
            "token": self.api_token,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(AHREFS_API_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            return make_error_response(
                code="provider_request_failed",
                message=f"Ahrefs API error: {exc}",
                provider="ahrefs",
                retryable=True,
            )

        backlinks = []
        overview = {}
        for row in data.get("backlinks", []):
            overview = row.get("target", {})
            backlinks.append(
                BacklinkEntry(
                    anchor=row.get("anchor", ""),
                    domain_rating=int(row.get("domain_rating", 0)),
                    url_from=row.get("url_from", ""),
                    url_to=row.get("url_to", ""),
                    title=row.get("url_to_title", ""),
                )
            )

        return BacklinkData(
            domain=domain,
            domain_rating=int(overview.get("domain_rating", 0)),
            total_backlinks=data.get("backlinks_count", 0),
            referring_domains=data.get("referring_domains_count", 0),
            top_backlinks=backlinks,
        )

    async def get_traffic(
        self, domain: str, country: str | None = None
    ) -> dict[str, Any]:
        """Get estimated organic traffic data."""
        if not self.api_token:
            return make_error_response(
                code="missing_api_key",
                message="AHREFS_API_TOKEN not configured",
                provider="ahrefs",
                details={"env_var": "AHREFS_API_TOKEN"},
            )
        return make_error_response(
            code="unsupported_capability",
            message="Traffic endpoint is not implemented for the current Ahrefs integration.",
            provider="ahrefs",
            details={"status": "beta"},
        )

    async def get_keyword_difficulty(
        self, keyword: str, country: str = "us"
    ) -> dict[str, Any]:
        """Get keyword difficulty score."""
        if not self.api_token:
            return make_error_response(
                code="missing_api_key",
                message="AHREFS_API_TOKEN not configured",
                provider="ahrefs",
                details={"env_var": "AHREFS_API_TOKEN"},
            )
        return make_error_response(
            code="unsupported_capability",
            message="Keyword difficulty is not implemented for the current Ahrefs integration.",
            provider="ahrefs",
            details={"status": "beta"},
        )

    async def compare_domains(self, domain1: str, domain2: str) -> dict[str, Any]:
        """Compare two domains."""
        d1 = await self.get_backlinks(domain1)
        d2 = await self.get_backlinks(domain2)

        if isinstance(d1, dict) and "error" in d1:
            return d1
        if isinstance(d2, dict) and "error" in d2:
            return d2

        # At this point d1 and d2 are BacklinkData
        assert not isinstance(d1, dict), "Expected BacklinkData"
        assert not isinstance(d2, dict), "Expected BacklinkData"

        return {
            "domain_rating": {
                domain1: d1.domain_rating,
                domain2: d2.domain_rating,
                "winner": domain1 if d1.domain_rating > d2.domain_rating else domain2,
            },
            "total_backlinks": {
                domain1: d1.total_backlinks,
                domain2: d2.total_backlinks,
            },
        }
