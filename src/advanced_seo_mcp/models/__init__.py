"""Pydantic models for SEO analysis results."""

from .common import SEOBaseModel, Issue
from .onpage import OnPageResult
from .technical import TechnicalAudit
from .psi import PageSpeedResult
from .ahrefs import BacklinkData, BacklinkEntry
from .report import SEOReport

__all__ = [
    "SEOBaseModel",
    "Issue",
    "OnPageResult",
    "TechnicalAudit",
    "PageSpeedResult",
    "BacklinkData",
    "BacklinkEntry",
    "SEOReport",
]
