"""Tests for config module."""

from advanced_seo_mcp.config import get_settings


def test_get_settings_returns_defaults():
    """Settings should return defaults when no env vars set."""
    settings = get_settings()
    assert settings.google_psi_api_key is None
    assert settings.ahrefs_api_token is None
    assert settings.http_timeout == 10.0
    assert settings.http_max_retries == 3
    assert settings.rate_limit_per_second == 2.0
    assert settings.max_sitemap_pages == 50
    assert settings.has_ahrefs is False
    assert settings.has_psi is False
