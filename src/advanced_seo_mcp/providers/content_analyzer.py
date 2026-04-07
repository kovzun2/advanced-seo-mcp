"""Content and keyword density analyzer provider."""

import string
from collections import Counter
from typing import Any

from bs4 import BeautifulSoup

from ..http_client import SafeHTTPClient
from .base import BaseProvider


class ContentAnalyzer(BaseProvider):
    """Analyzes keyword density and content metrics."""

    def __init__(self, http_client: SafeHTTPClient):
        super().__init__(http_client)

    async def analyze(self, url: str, target_keyword: str | None = None, **kwargs: Any) -> dict[str, Any]:
        """Analyze keyword density on page."""
        url = self._normalize_url(url)
        try:
            resp = await self.http.get(url)
        except Exception as exc:
            return {"error": str(exc)}

        soup = BeautifulSoup(resp.content, "lxml")
        for tag in soup(["script", "style"]):
            tag.extract()

        text = soup.get_text()
        translator = str.maketrans("", "", string.punctuation)
        clean = text.translate(translator).lower()
        words = [w for w in clean.split() if len(w) > 2]
        total = len(words)
        counts = Counter(words)

        top = counts.most_common(10)
        result = {
            "total_words": total,
            "top_keywords": [
                {"word": w, "count": c, "density": f"{(c / total) * 100:.2f}%"}
                for w, c in top
            ],
            "target_analysis": None,
        }

        if target_keyword:
            target = target_keyword.lower()
            count = clean.count(target)
            density = (count / total) * 100 if total > 0 else 0
            if 1 <= density <= 2.5:
                rec = "Good"
            elif density < 1:
                rec = "Low"
            else:
                rec = "High (Spam Risk)"
            result["target_analysis"] = {
                "keyword": target,
                "count": count,
                "density": f"{density:.2f}%",
                "recommendation": rec,
            }

        return result
