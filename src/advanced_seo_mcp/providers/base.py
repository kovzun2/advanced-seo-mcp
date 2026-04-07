"""Abstract base class for all SEO analysis providers."""

from abc import ABC, abstractmethod
from typing import Any

from ..http_client import SafeHTTPClient
from ..models.common import SEOBaseModel


class BaseProvider(ABC):
    """Base class for SEO providers.

    Each provider gets an HTTP client and implements `analyze()`.
    """

    def __init__(self, http_client: SafeHTTPClient):
        self.http = http_client

    @abstractmethod
    async def analyze(self, url: str, **kwargs: Any) -> SEOBaseModel | dict[str, str]:
        """Run analysis on the given URL and return a typed result."""
        ...

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Add https:// scheme if missing."""
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            return f"https://{url}"
        return url
