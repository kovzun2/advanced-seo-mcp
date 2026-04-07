# Advanced SEO MCP

[![Tests](https://github.com/kovzun2/advanced-seo-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/kovzun2/advanced-seo-mcp/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

MCP-сервер для профессионального SEO-анализа. Предоставляет ИИ-агентам 12 инструментов: от onpage-аудита и проверки бэклинков до анализа скорости загрузки и сравнения конкурентов.

## Возможности

| Инструмент | Описание | API-ключ |
|---|---|---|
| `onpage_audit` | Мета-теги, заголовки, контент, ссылки, alt-тексты | — |
| `technical_health_check` | robots.txt, sitemap, HTTPS, security-заголовки | — |
| `check_schema_markup` | Валидация JSON-LD разметки | — |
| `check_broken_links_on_page` | Поиск битых ссылок (404) | — |
| `analyze_content_density` | Плотность ключевых слов | — |
| `bulk_sitemap_audit` | Массовый аудит страниц по sitemap | — |
| `analyze_page_speed` | Google PageSpeed Insights, Core Web Vitals | `GOOGLE_PSI_API_KEY` |
| `get_backlinks` | Бэклинки, Domain Rating через Ahrefs | `AHREFS_API_TOKEN` |
| `compare_competitors` | Сравнение доменов по SEO-метрикам | `AHREFS_API_TOKEN` |
| `estimate_traffic` | Оценка органического трафика | `AHREFS_API_TOKEN` |
| `check_difficulty` | Сложность ключевого слова | `AHREFS_API_TOKEN` |
| `generate_audit_report` | Полный отчёт в Markdown | Частично |

6 из 12 инструментов работают без API-ключей.

## Установка

```bash
git clone https://github.com/kovzun2/advanced-seo-mcp.git
cd advanced-seo-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Настройка

Создайте файл `.env` на основе примера:

```bash
cp .env.example .env
```

| Переменная | Описание | Где взять |
|---|---|---|
| `GOOGLE_PSI_API_KEY` | Ключ Google PageSpeed Insights | [Google Cloud Console](https://console.cloud.google.com/) |
| `AHREFS_API_TOKEN` | Токен Ahrefs API | [Ahrefs API](https://ahrefs.com/api) |

Инструменты возвращают понятное сообщение, если API-ключ не настроен.

## Использование

Запустите сервер:

```bash
source .venv/bin/activate
python -m advanced_seo_mcp.server
```

Сервер работает через STDIO и подключается к MCP-клиенту (Gemini CLI, Cursor, Claude Desktop и др.). После подключения ИИ-агент может вызывать инструменты напрямую:

```
Сделай onpage-аудит https://example.com/blog/post-1
```

```
Сравни example.com и competitor.com по бэклинкам и трафику
```

```
Сгенерируй полный SEO-отчёт для example.com
```

## Архитектура

```
┌─────────────────────────────┐
│      MCP-клиент (LLM)      │
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│  server.py — 12 инструментов│
│  с валидацией (Pydantic)    │
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│  ReportOrchestrator         │
│  (параллельное выполнение)  │
└──┬────┬────┬────┬────┬──────┘
   │    │    │    │    │
 OnPage Tech PSI Link Ahrefs
   │    │    │    │    │
   └────┴────┴────┴────┘
               │
┌──────────────▼──────────────┐
│  SafeHTTPClient             │
│  · SSRF-защита              │
│  · Retry с exponential backoff │
│  · Rate limiting            │
│  · Ротация User-Agent       │
└──────────────┬──────────────┘
               │
     ┌─────────┴─────────┐
     ▼                   ▼
Google PSI API      Ahrefs API v2
```

## Структура проекта

```
├── src/advanced_seo_mcp/
│   ├── server.py              # MCP-сервер (12 инструментов)
│   ├── config.py              # Настройки (pydantic-settings)
│   ├── http_client.py         # Безопасный HTTP-клиент
│   ├── models/                # Pydantic-модели данных
│   └── providers/             # Провайдеры анализа
├── tests/                     # Тесты (37)
├── .env.example               # Пример конфигурации
├── pyproject.toml             # Зависимости
└── .github/workflows/         # CI/CD
```

## Разработка

### Зависимости для разработки

```bash
pip install -e ".[dev]"
```

### Тесты

```bash
pytest -v
```

### Линтер и форматтер

```bash
ruff check src/ tests/        # проверка
ruff check --fix src/ tests/  # автофикс
ruff format src/ tests/       # форматирование
```

### Проверка типов

```bash
mypy src/ --ignore-missing-imports
```

### Pre-commit

```bash
pre-commit install
```

## Зависимости

| Пакет | Версия | Назначение |
|---|---|---|
| fastmcp | >=2.10.0 | MCP-сервер |
| httpx | >=0.27.0 | Async HTTP |
| beautifulsoup4 | >=4.12.0 | Парсинг HTML |
| lxml | >=5.0.0 | Парсинг XML/HTML |
| pydantic | >=2.0.0 | Модели и валидация |
| pydantic-settings | >=2.0.0 | Загрузка настроек |

Полный список — в [pyproject.toml](pyproject.toml).

## Безопасность

- **SSRF-защита** — блокировка запросов к внутренним IP (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- **DNS-проверка** — разрешение имён и проверка на приватные IP
- **Валидация схем** — только `http://` и `https://`
- **Rate limiting** — ограничение частоты запросов
- **API-ключи** — хранятся только в `.env` (в `.gitignore`)

## Отличия от оригинала

Форк [halilertekin/advanced-seo-mcp](https://github.com/halilertekin/advanced-seo-mcp) с полным рефакторингом:

| | Оригинал | Этот форк |
|---|---|---|
| Тесты | 0 | 37 |
| Типизация | `Dict[str, Any]` | Pydantic-модели |
| HTTP | requests (sync) | httpx (async) |
| Ahrefs | CapSolver (обход CAPTCHA) | Официальный API v2 |
| SSRF-защита | Нет | Есть |
| CI/CD | Нет | GitHub Actions |

## Лицензия

[MIT](LICENSE)

## Вклад

См. [CONTRIBUTING.md](CONTRIBUTING.md).
