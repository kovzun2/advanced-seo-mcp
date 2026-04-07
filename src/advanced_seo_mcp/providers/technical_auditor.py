"""Technical SEO auditor provider."""

from typing import Any
from urllib.parse import urlparse

from ..http_client import SafeHTTPClient
from ..models.common import Issue
from ..models.technical import TechnicalAudit
from .base import BaseProvider


class TechnicalAuditor(BaseProvider):
    """Checks technical SEO factors: robots.txt, sitemap, security headers."""

    def __init__(self, http_client: SafeHTTPClient):
        super().__init__(http_client)

    async def analyze(self, url: str, **kwargs: Any) -> TechnicalAudit:
        """Run technical SEO audit."""
        url = self._normalize_url(url)
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        issues: list[Issue] = []
        score = 100

        # robots.txt
        has_robots = False
        robots_size = 0
        try:
            resp = await self.http.get(f"{base}/robots.txt")
            has_robots = resp.status_code == 200
            robots_size = len(resp.content) if has_robots else 0
        except Exception:
            issues.append(Issue(message="robots.txt not found", severity="warning"))
            score -= 10

        # sitemap.xml
        has_sitemap = False
        sitemap_url = None
        for path in ["/sitemap.xml", "/sitemap_index.xml", "/wp-sitemap.xml"]:
            try:
                resp = await self.http.head(f"{base}{path}")
                if resp.status_code == 200:
                    has_sitemap = True
                    sitemap_url = f"{base}{path}"
                    break
            except Exception:
                continue
        if not has_sitemap:
            issues.append(Issue(message="No sitemap found", severity="warning"))
            score -= 10

        # Security headers
        https = parsed.scheme == "https"
        hsts = False
        x_frame = None
        xcto = None

        try:
            resp = await self.http.head(url)
            hsts = "strict-transport-security" in resp.headers
            x_frame = resp.headers.get("X-Frame-Options")
            xcto = resp.headers.get("X-Content-Type-Options")
        except Exception:
            issues.append(Issue(message="Could not fetch headers", severity="info"))

        if not https:
            issues.append(Issue(message="HTTPS not enabled", severity="critical"))
            score -= 25
        if not hsts:
            issues.append(Issue(message="HSTS header missing", severity="warning"))
            score -= 10
        if not x_frame:
            issues.append(Issue(message="X-Frame-Options missing", severity="info"))
            score -= 5
        if not xcto:
            issues.append(
                Issue(message="X-Content-Type-Options missing", severity="info")
            )
            score -= 5

        score = max(0, score)

        return TechnicalAudit(
            domain=parsed.netloc,
            has_robots_txt=has_robots,
            robots_txt_size=robots_size,
            has_sitemap=has_sitemap,
            sitemap_url=sitemap_url,
            https_enabled=https,
            hsts_enabled=hsts,
            x_frame_options=x_frame,
            x_content_type_options=xcto,
            issues=issues,
            score=score,
        )
