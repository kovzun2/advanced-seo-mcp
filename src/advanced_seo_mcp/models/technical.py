"""Technical SEO audit models."""

from pydantic import Field

from .common import SEOBaseModel, Issue


class TechnicalAudit(SEOBaseModel):
    """Technical SEO health assessment."""

    domain: str

    # Core files
    has_robots_txt: bool
    robots_txt_size: int = Field(ge=0, default=0)
    has_sitemap: bool
    sitemap_url: str | None = None
    final_url: str | None = None
    canonical_host: str | None = None
    redirect_count: int = Field(ge=0, default=0)
    redirects_to_https: bool = False

    # Security
    https_enabled: bool
    hsts_enabled: bool
    x_frame_options: str | None = None
    x_content_type_options: str | None = None
    indexable: bool = True
    robots_meta: str | None = None

    # Diagnostics
    issues: list[Issue] = Field(default_factory=list)
    score: int = Field(ge=0, le=100)
