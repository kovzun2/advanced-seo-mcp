# Advanced SEO MCP

Professional SEO analysis MCP server for AI agents. Provides on-page analysis, technical audits, Google PageSpeed Insights, and Ahrefs API integration.

## Features

| Tool | Description |
|------|-------------|
| `onpage_audit` | Meta tags, headings, content, links, images |
| `technical_health_check` | robots.txt, sitemap, HTTPS, security headers |
| `analyze_page_speed` | Google PSI — Core Web Vitals |
| `check_schema_markup` | JSON-LD validation |
| `check_broken_links_on_page` | 404 link detection |
| `analyze_content_density` | Keyword density analysis |
| `bulk_sitemap_audit` | Multi-page audit via sitemap |
| `get_backlinks` | Ahrefs backlink data |
| `compare_competitors` | Domain comparison via Ahrefs |
| `generate_audit_report` | Full Markdown report |

## Installation

### Manual
```bash
git clone https://github.com/kovzun2/advanced-seo-mcp.git
cd advanced-seo-mcp
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Configuration

```bash
cp .env.example .env
# Edit .env with your API keys
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_PSI_API_KEY` | For PSI tools | [Get here](https://developers.google.com/speed/docs/insights/v5/get-started) |
| `AHREFS_API_TOKEN` | For Ahrefs tools | [Get here](https://ahrefs.com/api) |

Tools gracefully degrade with a helpful message if API keys are missing.

## Development

```bash
# Install dev deps
pip install -e ".[dev]"

# Run tests
pytest -v

# Lint
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/

# Install pre-commit hooks
pre-commit install
```

## Architecture

```
MCP Client (LLM)
       │
  server.py — 12 MCP tools
       │
  ReportOrchestrator (parallel execution)
       │
  ┌────┬────┬────┬────┬────┐
OnPage Tech PSI  Link Sitemap
       │
  SafeHTTPClient (SSRF protection, retry, rate limit)
       │
  External APIs: Google PSI, Ahrefs v2
```

## License

MIT
