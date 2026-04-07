"""Google PageSpeed Insights analyzer provider."""

from typing import Any

from ..config import get_settings
from ..http_client import SafeHTTPClient
from ..models.psi import PageSpeedResult
from .base import BaseProvider


class PSIAnalyzer(BaseProvider):
    """Analyzes page speed via Google PageSpeed Insights API."""

    def __init__(self, http_client: SafeHTTPClient):
        super().__init__(http_client)

    async def analyze(self, url: str, strategy: str = "mobile", **kwargs: Any) -> PageSpeedResult | dict[str, str]:
        """Run PageSpeed analysis."""
        url = self._normalize_url(url)
        settings = get_settings()

        if not settings.has_psi:
            return {"error": "GOOGLE_PSI_API_KEY not configured — get one at https://developers.google.com/speed/docs/insights/v5/get-started"}

        endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            "url": url,
            "strategy": strategy,
            "key": settings.google_psi_api_key,
            "category": ["performance", "seo"],
        }

        try:
            resp = await self.http.get(endpoint, params=params)
            data = resp.json()
        except Exception as exc:
            return {"error": f"PageSpeed API error: {exc}"}

        lighthouse = data.get("lighthouseResult", {})
        audits = lighthouse.get("audits", {})
        categories = lighthouse.get("categories", {})

        def get_val(name: str) -> str:
            return audits.get(name, {}).get("displayValue", "N/A")

        perf_score = categories.get("performance", {}).get("score", 0)
        seo_score = categories.get("seo", {}).get("score", 0)

        return PageSpeedResult(
            strategy=strategy,
            performance_score=int(perf_score * 100),
            seo_score=int(seo_score * 100),
            lcp=get_val("largest-contentful-paint"),
            fcp=get_val("first-contentful-paint"),
            cls=get_val("cumulative-layout-shift"),
            inp=get_val("interaction-to-next-paint"),
        )
