"""Centralized application settings via pydantic-settings."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Keys (optional — graceful degradation if missing)
    google_psi_api_key: str | None = Field(
        default=None,
        description="Google PageSpeed Insights API key",
    )
    ahrefs_api_token: str | None = Field(
        default=None,
        description="Ahrefs API token (free tier available)",
    )

    # HTTP client tweaks
    http_timeout: float = Field(default=10.0, ge=1.0, le=60.0)
    http_max_retries: int = Field(default=3, ge=0, le=10)
    rate_limit_per_second: float = Field(default=2.0, gt=0)

    # Provider limits
    max_sitemap_pages: int = Field(default=50, ge=1, le=200)

    # Paths
    cache_db_path: Path = Field(
        default=Path.home() / ".advanced_seo_mcp_cache.db",
    )
    reports_dir: Path = Field(default=Path("reports"))

    @property
    def has_ahrefs(self) -> bool:
        return self.ahrefs_api_token is not None

    @property
    def has_psi(self) -> bool:
        return self.google_psi_api_key is not None


_settings: Settings | None = None


def get_settings() -> Settings:
    """Lazy-load and cache the singleton Settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset cached settings. Useful for tests that modify environment."""
    global _settings
    _settings = None
