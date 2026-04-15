"""Common Pydantic models shared across providers."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SEOBaseModel(BaseModel):
    """Base model for all SEO analysis results. Immutable, no extra fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class Issue(SEOBaseModel):
    """A single SEO issue with severity."""

    message: str
    severity: str = Field(pattern="^(critical|warning|info)$")


class ErrorDetails(SEOBaseModel):
    """Normalized error payload returned by tools."""

    code: str
    message: str
    retryable: bool = False
    provider: str
    details: dict[str, Any] = Field(default_factory=dict)
