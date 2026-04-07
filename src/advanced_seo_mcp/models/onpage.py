"""On-page SEO analysis models."""

from pydantic import Field

from .common import SEOBaseModel, Issue


class OnPageResult(SEOBaseModel):
    """Complete on-page SEO analysis of a single URL."""

    url: str
    status_code: int
    response_time_ms: float = Field(ge=0)

    # Meta tags
    meta_title: str | None = Field(default=None, max_length=200)
    meta_title_length: int = Field(ge=0)
    meta_title_optimal: bool
    meta_description: str | None = Field(default=None, max_length=500)
    meta_description_length: int = Field(ge=0)
    meta_description_optimal: bool
    canonical: str | None = None
    robots: str = "index, follow"

    # Headings
    h1_count: int = Field(ge=0)
    h1_tags: list[str] = Field(default_factory=list)
    h2_count: int = Field(ge=0)
    h2_tags: list[str] = Field(default_factory=list)

    # Content
    word_count: int = Field(ge=0)
    thin_content: bool

    # Links
    total_links: int = Field(ge=0)
    internal_links: int = Field(ge=0)
    external_links: int = Field(ge=0)

    # Images
    total_images: int = Field(ge=0)
    images_missing_alt: int = Field(ge=0)

    # Diagnostics
    issues: list[Issue] = Field(default_factory=list)
