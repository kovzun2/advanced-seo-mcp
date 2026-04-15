"""Content and keyword density analyzer provider."""

import re
import string
from collections import Counter
from typing import Any

from bs4 import BeautifulSoup

from ..http_client import SafeHTTPClient
from ..responses import make_error_response
from .base import BaseProvider


class ContentAnalyzer(BaseProvider):
    """Analyzes keyword density and content metrics."""

    def __init__(self, http_client: SafeHTTPClient):
        super().__init__(http_client)

    async def analyze(
        self, url: str, target_keyword: str | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Analyze keyword density on page."""
        url = self._normalize_url(url)
        try:
            resp = await self.http.get(url)
        except Exception as exc:
            return make_error_response(
                code="fetch_failed",
                message=str(exc),
                provider="content",
                retryable=True,
            )

        soup = BeautifulSoup(resp.content, "lxml")
        for tag in soup(["script", "style"]):
            tag.extract()

        text = soup.get_text(separator=" ", strip=True)
        translator = str.maketrans("", "", string.punctuation)
        clean = text.translate(translator).lower()
        words = [w for w in clean.split() if len(w) > 2]
        total = len(words)
        counts = Counter(words)
        unique_words = len(counts)
        bigrams = Counter(" ".join(pair) for pair in zip(words, words[1:]))

        top = counts.most_common(10)
        result = {
            "total_words": total,
            "unique_words": unique_words,
            "lexical_diversity": f"{(unique_words / total) * 100:.2f}%" if total else "0.00%",
            "top_keywords": [
                {"word": w, "count": c, "density": f"{(c / total) * 100:.2f}%"}
                for w, c in top
            ],
            "top_bigrams": [
                {"phrase": phrase, "count": count}
                for phrase, count in bigrams.most_common(5)
                if count > 1
            ],
            "target_analysis": None,
        }

        if target_keyword:
            target = " ".join(target_keyword.lower().split())
            normalized_text = re.sub(r"\s+", " ", clean).strip()
            target_tokens = [part for part in target.split() if part]
            if target_tokens:
                phrase_windows = zip(
                    *[words[index:] for index in range(len(target_tokens))]
                )
                count = sum(
                    1
                    for window in phrase_windows
                    if list(window) == target_tokens
                )
            else:
                count = 0
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
                "match_type": "phrase" if len(target_tokens) > 1 else "token",
                "normalized_text_length": len(normalized_text),
            }

        return result
