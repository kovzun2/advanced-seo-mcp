# 🔍 Advanced SEO MCP

> **Профессиональный SEO-анализ для ИИ-агентов** — 12 инструментов для аудита сайтов прямо из чата с AI.

---

## 📖 Что это такое?

Это сервер **MCP** (Model Context Protocol) — мост между ИИ-агентом (Gemini CLI, Cursor, Claude Desktop и др.) и профессиональными SEO-инструментами.

**Простыми словами:** вы говорите ИИ-агенту *«проверь SEO моего сайта»*, а он запускает реальные инструменты анализа и возвращает подробный отчёт.

### Что умеет

| Инструмент | Что проверяет | Нужен ли API-ключ? |
|---|---|---|
| `onpage_audit` | Мета-теги, заголовки, контент, ссылки, картинки | ❌ |
| `technical_health_check` | robots.txt, sitemap, HTTPS, security-заголовки | ❌ |
| `check_schema_markup` | JSON-LD разметка (schema.org) | ❌ |
| `check_broken_links_on_page` | Битые ссылки (404) на странице | ❌ |
| `analyze_content_density` | Плотность ключевых слов | ❌ |
| `bulk_sitemap_audit` | Массовый аудит страниц по sitemap | ❌ |
| `analyze_page_speed` | Скорость загрузки (Google PageSpeed Insights) | ✅ Google PSI |
| `get_backlinks` | Бэклинки и Domain Rating | ✅ Ahrefs |
| `compare_competitors` | Сравнение двух доменов | ✅ Ahrefs |
| `estimate_traffic` | Оценка органического трафика | ✅ Ahrefs |
| `check_difficulty` | Сложность ключевого слова | ✅ Ahrefs |
| `generate_audit_report` | Полный SEO-отчёт в Markdown | Частично |

> **💡 Без API-ключей** работают 6 из 12 инструментов — достаточно для базового аудита.

---

## 🚀 Быстрый старт

### Шаг 1: Клонирование

```bash
git clone https://github.com/kovzun2/advanced-seo-mcp.git
cd advanced-seo-mcp
```

### Шаг 2: Установка зависимостей

```bash
# Создаём виртуальное окружение
python3 -m venv .venv

# Активируем
source .venv/bin/activate

# Устанавливаем проект
pip install -e .
```

> **Новичкам:** если `python3` не найден, попробуйте `python`. Если `pip` ругается — убедитесь, что установлен Python 3.10 или новее: `python3 --version`

### Шаг 3: Настройка API-ключей (опционально)

```bash
# Копируем пример конфигурации
cp .env.example .env

# Открываем в редакторе и вставляем ключи
nano .env
```

Файл `.env` выглядит так:

```env
# Google PageSpeed Insights — бесплатный, 25 000 запросов/день
GOOGLE_PSI_API_KEY=ваш_ключ

# Ahrefs — бесплатный план: 1 000 строк/день
AHREFS_API_TOKEN=ваш_токен
```

#### Где взять ключи

**Google PSI API Key:**
1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте проект (или выберите существующий)
3. Включите API «PageSpeed Insights API»
4. Создайте учётные данные → API-ключ
5. Вставьте ключ в `.env`

**Ahrefs API Token:**
1. Зарегистрируйтесь на [ahrefs.com/api](https://ahrefs.com/api)
2. Бесплатный план: 1 000 строк/день
3. Скопируйте токен в `.env`

---

## 💻 Как использовать

### Через Gemini CLI

Если у вас установлен [Gemini CLI](https://github.com/google-gemini/gemini-cli):

```bash
gemini
```

Затем в чате просто напишите:

```
Проверь SEO сайта example.com
```

ИИ-агент сам вызовет нужные инструменты.

### Как самостоятельный сервер

```bash
# Активируйте окружение
source .venv/bin/activate

# Запустите сервер
python -m advanced_seo_mcp.server
```

Сервер запустится в режиме STDIO и будет ждать подключений от MCP-клиента.

---

## 📋 Примеры запросов к ИИ-агенту

### Базовый аудит (без API-ключей)

```
Сделай onpage-аудит https://mysite.ru/blog/post-1
```

```
Проверь технические SEO сайта example.com
```

```
Найди битые ссылки на странице https://example.com/about
```

### Полный аудит (с API-ключами)

```
Сгенерируй полный SEO-отчёт для example.com
```

```
Сравни example.com и competitor.com по бэклинкам и трафику
```

```
Какая сложность у ключевого слова "seo tools" в США?
```

---

## 🏗️ Архитектура

```
┌──────────────────────────────────────────────┐
│            ИИ-агент (Gemini CLI)             │
│  «Проверь SEO сайта example.com»            │
└──────────────────┬───────────────────────────┘
                   │ MCP Protocol (STDIO)
┌──────────────────▼───────────────────────────┐
│              server.py                       │
│  12 MCP-инструментов с валидацией входных    │
│  данных (Pydantic Annotated[...])           │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│         ReportOrchestrator                   │
│  Запускает независимые проверки параллельно  │
│  через asyncio.gather()                      │
└──┬────┬────┬────┬────┬────┬──────────────────┘
   │    │    │    │    │    │
 OnPage Tech PSI Link Site Ahrefs
   │    │    │    │    │    │
   └────┴────┴────┴────┴────┘
                   │
┌──────────────────▼───────────────────────────┐
│            SafeHTTPClient                    │
│  • SSRF-защита (блокировка внутренних IP)   │
│  • Retry с exponential backoff               │
│  • Rate limiting (token bucket)              │
│  • Ротация User-Agent                        │
└──────────────────┬───────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
  Google PSI API       Ahrefs API v2
  (скорость сайта)     (бэклинки, трафик)
```

### Структура проекта

```
advanced-seo-mcp/
├── src/advanced_seo_mcp/
│   ├── server.py              # MCP-сервер (12 инструментов)
│   ├── config.py              # Настройки (pydantic-settings)
│   ├── http_client.py         # Безопасный HTTP-клиент
│   │
│   ├── models/                # Pydantic-модели данных
│   │   ├── common.py          # Базовые модели (Issue, SEOBaseModel)
│   │   ├── onpage.py          # OnPageResult
│   │   ├── technical.py       # TechnicalAudit
│   │   ├── psi.py             # PageSpeedResult
│   │   ├── ahrefs.py          # BacklinkData
│   │   └── report.py          # SEOReport
│   │
│   └── providers/             # Провайдеры анализа
│       ├── base.py            # Абстрактный базовый класс
│       ├── onpage_analyzer.py
│       ├── technical_auditor.py
│       ├── psi_analyzer.py
│       ├── link_inspector.py
│       ├── schema_validator.py
│       ├── content_analyzer.py
│       ├── sitemap_auditor.py
│       ├── ahrefs_api.py      # Официальный Ahrefs API
│       ├── competitor_analyzer.py
│       └── reporter.py        # ReportOrchestrator + MarkdownFormatter
│
├── tests/                     # Тесты (37 штук)
│   ├── conftest.py
│   ├── fixtures/              # Тестовые данные
│   └── test_*.py
│
├── .env.example               # Пример конфигурации
├── pyproject.toml             # Зависимости проекта
└── .github/workflows/         # CI/CD (автоматические тесты)
```

---

## 🛠️ Разработка

### Установка dev-зависимостей

```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

### Запуск тестов

```bash
pytest -v
```

Ожидаемый результат: **37 тестов, 0 проваленных**.

### Линтер и форматтер

Проект использует **Ruff** — быстрый линтер и форматтер:

```bash
# Проверить стиль
ruff check src/ tests/

# Исправить автоматически
ruff check --fix src/ tests/

# Форматировать код
ruff format src/ tests/
```

### Проверка типов

```bash
mypy src/ --ignore-missing-imports
```

### Pre-commit хуки

Автоматическая проверка при каждом коммите:

```bash
pre-commit install
```

Теперь при `git commit` автоматически запустятся ruff и тесты.

---

## 🔒 Безопасность

Проект спроектирован с учётом безопасности:

| Защита | Описание |
|---|---|
| **SSRF-защита** | Блокировка запросов к внутренним IP (127.0.0.0/8, 10.0.0.0/8, и т.д.) |
| **DNS-проверка** | Разрешение имён хостов и проверка на приватные IP |
| **Валидация схем** | Только `http://` и `https://` — никаких `file://`, `ftp://` |
| **Rate limiting** | Ограничение частоты запросов (по умолчанию 2 запроса/сек) |
| **Retry с backoff** | Автоматические повторные попытки при ошибках |
| **API-ключи в .env** | Никогда не коммитятся (в `.gitignore`) |

---

## 🆚 Что изменено по сравнению с оригиналом

Этот проект — форк [halilertekin/advanced-seo-mcp](https://github.com/halilertekin/advanced-seo-mcp) с полным рефакторингом:

| | Было (оригинал) | Стало (этот форк) |
|---|---|---|
| **Тесты** | 0 | 37 |
| **Типизация** | `Dict[str, Any]` | Pydantic-модели с валидацией |
| **HTTP-клиент** | `requests` (синхронный) | `httpx` (async) |
| **Ahrefs** | CapSolver (обход CAPTCHA) | Официальный API v2 |
| **SSRF-защита** | ❌ Отсутствует | ✅ Блокировка приватных IP |
| **Валидация URL** | ❌ Нет | ✅ Pydantic Annotated |
| **CI/CD** | ❌ Нет | ✅ GitHub Actions |
| **Зависимости** | Сломанные (несуществующие версии) | ✅ Рабочие |
| **Обработка ошибок** | `except: pass` | `except Exception` + логирование |
| **Линтер** | ❌ Нет | ✅ ruff + mypy |

---

## 📦 Зависимости

### Основные

| Пакет | Версия | Зачем |
|---|---|---|
| `fastmcp` | >=2.10.0 | MCP-сервер |
| `httpx` | >=0.27.0 | Async HTTP-клиент |
| `beautifulsoup4` | >=4.12.0 | Парсинг HTML |
| `lxml` | >=5.0.0 | Быстрый XML/HTML парсер |
| `pydantic` | >=2.0.0 | Валидация и модели данных |
| `pydantic-settings` | >=2.0.0 | Загрузка настроек из .env |
| `fake-useragent` | >=1.5.0 | Ротация User-Agent |

### Для разработки

| Пакет | Зачем |
|---|---|
| `pytest` | Тесты |
| `pytest-asyncio` | Async-тесты |
| `pytest-cov` | Покрытие кода |
| `respx` | Мок HTTP-запросов |
| `ruff` | Линтер + форматтер |
| `mypy` | Проверка типов |
| `pre-commit` | Git-хуки |

---

## ❓ Часто задаваемые вопросы

### Что такое MCP?

**MCP** (Model Context Protocol) — это стандартный протокол, позволяющий ИИ-агентам использовать внешние инструменты. Представьте его как «розетку» — подключаете сервер и получаете новые возможности.

### Нужен ли сервер для запуска?

Нет. MCP-сервер работает как обычный процесс и общается через STDIO. Вам не нужно поднимать веб-сервер.

### Что если у меня нет API-ключей?

6 из 12 инструментов работают без ключей. Вы получите базовый SEO-аудит: мета-теги, заголовки, битые ссылки, техническое здоровье.

### Безопасно ли хранить API-ключи в .env?

Да, если файл `.env` добавлен в `.gitignore` (он добавлен). Ключи никогда не попадут в репозиторий.

### Можно ли использовать с Cursor / Claude Desktop?

Да. Любой MCP-клиент может подключиться. Настройте путь к серверу в конфигурации вашего клиента.

---

## 📄 Лицензия

[MIT](LICENSE) — используйте свободно.

---

## 🤝 Как внести вклад

Подробности в [CONTRIBUTING.md](CONTRIBUTING.md).

Коротко:

1. Форкните репозиторий
2. Создайте ветку (`git checkout -b feature/my-feature`)
3. Внесите изменения
4. Убедитесь, что тесты проходят: `pytest -v`
5. Создайте Pull Request
