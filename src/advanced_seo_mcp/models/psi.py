"""Google PageSpeed Insights result models."""

from pydantic import Field

from .common import SEOBaseModel


class PageSpeedResult(SEOBaseModel):
    """Core Web Vitals and performance metrics from Google PSI."""

    strategy: str = Field(pattern="^(mobile|desktop)$")
    performance_score: int = Field(ge=0, le=100)
    seo_score: int = Field(ge=0, le=100)

    # Core Web Vitals
    lcp: str
    fcp: str
    cls: str
    inp: str
