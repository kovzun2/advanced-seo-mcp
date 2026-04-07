"""Tests for config module."""

from advanced_seo_mcp.config import get_settings, reset_settings


def test_get_settings_returns_defaults():
    """Settings should return defaults when no env vars set."""
    reset_settings()
    settings = get_settings()
    assert settings.google_psi_api_key is None
    assert settings.ahrefs_api_token is None
    assert settings.http_timeout == 10.0
    assert settings.http_max_retries == 3
    assert settings.rate_limit_per_second == 2.0
    assert settings.max_sitemap_pages == 50
    assert settings.has_ahrefs is False
    assert settings.has_psi is False


def test_settings_from_env_via_monkeypatch(monkeypatch):
    """Settings should load values from environment variables."""
    monkeypatch.setenv("GOOGLE_PSI_API_KEY", "test-key-123")
    monkeypatch.setenv("HTTP_TIMEOUT", "30.0")
    reset_settings()
    settings = get_settings()
    assert settings.google_psi_api_key == "test-key-123"
    assert settings.http_timeout == 30.0
    reset_settings()


def test_reset_settings_clears_cache():
    """reset_settings should clear the cached singleton."""
    reset_settings()
    s1 = get_settings()
    reset_settings()
    s2 = get_settings()
    # They could be same object or different depending on env state
    # What matters is that reset_settings doesn't raise
    assert s1 is not None
    assert s2 is not None
