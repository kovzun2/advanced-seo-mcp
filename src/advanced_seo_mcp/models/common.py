"""Common Pydantic models shared across providers."""

from pydantic import BaseModel, ConfigDict, Field


class SEOBaseModel(BaseModel):
    """Base model for all SEO analysis results. Immutable, no extra fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class Issue(SEOBaseModel):
    """A single SEO issue with severity."""

    message: str
    severity: str = Field(pattern="^(critical|warning|info)$")
