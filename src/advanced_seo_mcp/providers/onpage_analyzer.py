"""On-page SEO analyzer provider."""

from typing import Any, cast
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from ..http_client import SafeHTTPClient
from ..models.common import Issue
from ..models.onpage import OnPageResult
from .base import BaseProvider


class OnPageAnalyzer(BaseProvider):
    """Analyzes on-page SEO factors for a single URL."""

    def __init__(self, http_client: SafeHTTPClient):
        super().__init__(http_client)

    async def analyze(self, url: str, **kwargs: Any) -> OnPageResult | dict[str, str]:
        """Run on-page SEO analysis."""
        url = self._normalize_url(url)
        issues: list[Issue] = []

        try:
            resp = await self.http.get(url)
        except Exception as exc:
            return {"error": f"Failed to fetch URL: {exc}"}

        soup = BeautifulSoup(resp.content, "lxml")
        domain = urlparse(str(resp.url)).netloc

        # Meta tags
        title_tag = soup.title
        title_text = title_tag.get_text(strip=True) if title_tag else None
        title_len = len(title_text) if title_text else 0
        title_optimal = 30 <= title_len <= 60

        desc_tag = soup.find("meta", attrs={"name": "description"})
        desc_text = cast("str | None", desc_tag.get("content")) if desc_tag else None
        desc_len = len(desc_text) if desc_text else 0
        desc_optimal = 120 <= desc_len <= 160

        canonical_tag = soup.find("link", rel="canonical")
        canonical = (
            cast("str | None", canonical_tag.get("href")) if canonical_tag else None
        )

        robots_tag = soup.find("meta", attrs={"name": "robots"})
        robots = (
            str(robots_tag.get("content", "index, follow"))
            if robots_tag
            else "index, follow"
        )

        # Headings
        h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
        h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2")]

        if len(h1_tags) == 0:
            issues.append(Issue(message="No H1 tag found", severity="critical"))
        elif len(h1_tags) > 1:
            issues.append(
                Issue(
                    message=f"Multiple H1 tags found ({len(h1_tags)})",
                    severity="warning",
                )
            )

        # Content
        text = soup.get_text(separator=" ", strip=True)
        word_count = len(text.split())
        thin = word_count < 300
        if thin:
            issues.append(
                Issue(
                    message=f"Thin content: only {word_count} words", severity="warning"
                )
            )

        # Links
        all_links = soup.find_all("a", href=True)
        internal = 0
        external = 0
        for link in all_links:
            href = str(link["href"])
            full = urljoin(str(resp.url), href)
            parsed = urlparse(full)
            if parsed.scheme in ("http", "https"):
                if parsed.netloc == domain:
                    internal += 1
                else:
                    external += 1

        # Images
        images = soup.find_all("img")
        missing_alt = sum(1 for img in images if not img.get("alt"))
        if missing_alt > 0:
            issues.append(
                Issue(message=f"{missing_alt} images missing alt text", severity="info")
            )

        return OnPageResult(
            url=str(resp.url),
            status_code=resp.status_code,
            response_time_ms=resp.elapsed.total_seconds() * 1000,
            meta_title=title_text,
            meta_title_length=title_len,
            meta_title_optimal=title_optimal,
            meta_description=desc_text,
            meta_description_length=desc_len,
            meta_description_optimal=desc_optimal,
            canonical=canonical,
            robots=robots,
            h1_count=len(h1_tags),
            h1_tags=h1_tags,
            h2_count=len(h2_tags),
            h2_tags=h2_tags,
            word_count=word_count,
            thin_content=thin,
            total_links=len(all_links),
            internal_links=internal,
            external_links=external,
            total_images=len(images),
            images_missing_alt=missing_alt,
            issues=issues,
        )
