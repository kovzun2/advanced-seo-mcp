"""Smoke test for MCP server — verifies imports and tool registration."""

import asyncio


def test_server_imports():
    """Server module should import without errors."""
    from advanced_seo_mcp.server import mcp
    assert mcp is not None


def test_tools_registered():
    """All expected MCP tools should be registered."""
    from advanced_seo_mcp.server import mcp

    async def check():
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(check())
    expected = [
        "generate_audit_report",
        "analyze_page_speed",
        "check_schema_markup",
        "check_broken_links_on_page",
        "analyze_content_density",
        "compare_competitors",
        "bulk_sitemap_audit",
        "onpage_audit",
        "technical_health_check",
        "get_backlinks",
        "estimate_traffic",
        "check_difficulty",
    ]
    for name in expected:
        assert name in tool_names, f"Tool '{name}' not registered"
