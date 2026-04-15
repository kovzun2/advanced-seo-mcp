"""Full SEO report model combining all analyses."""

from datetime import datetime
from typing import Any

from pydantic import Field

from .common import SEOBaseModel
from .onpage import OnPageResult
from .technical import TechnicalAudit
from .psi import PageSpeedResult
from .ahrefs import BacklinkData


class SEOReport(SEOBaseModel):
    """Complete SEO report combining all provider results."""

    generated_at: datetime
    url: str
    domain: str

    onpage: OnPageResult | None = None
    technical: TechnicalAudit | None = None
    page_speed: PageSpeedResult | None = None
    backlinks: BacklinkData | None = None
    supplemental_sections: dict[str, Any] = Field(default_factory=dict)
    completed_checks: list[str] = Field(default_factory=list)
    skipped_checks: list[str] = Field(default_factory=list)
    partial: bool = False
    report_path: str | None = None

    overall_score: int = Field(ge=0, le=100)
    summary: str
