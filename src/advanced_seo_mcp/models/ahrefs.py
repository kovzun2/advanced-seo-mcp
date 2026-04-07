"""Ahrefs API data models."""

from pydantic import Field

from .common import SEOBaseModel


class BacklinkEntry(SEOBaseModel):
    """Single backlink from Ahrefs."""
    anchor: str
    domain_rating: int = Field(ge=0, le=100)
    url_from: str
    url_to: str
    title: str = ""


class BacklinkData(SEOBaseModel):
    """Ahrefs backlink overview for a domain."""
    domain: str
    domain_rating: int = Field(ge=0, le=100)
    total_backlinks: int = Field(ge=0)
    referring_domains: int = Field(ge=0)
    top_backlinks: list[BacklinkEntry] = Field(default_factory=list)
