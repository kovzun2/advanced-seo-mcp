# Roadmap

Рабочий roadmap для доведения `advanced-seo-mcp` до зрелого OSS MCP-продукта.

Правило ведения:
- Отмечать пункт только после фактического выполнения и минимальной проверки.
- Если пункт оказался слишком крупным, дробить его на отдельные подпункты в этом же файле до начала реализации.
- После завершения этапа коротко фиксировать результат и дату в секции `Progress Notes`.

## Stage 1: Product Hardening

### Public Contract
- [x] Ввести единый `_meta` для tool-ответов.
- [x] Ввести нормализованный `error` contract.
- [x] Привести README к честному описанию текущих возможностей.
- [ ] Задокументировать response examples для всех 12 инструментов.
- [ ] Зафиксировать compatibility policy для будущих изменений ответов.
- [ ] Добавить явный статус `stable` / `beta` / `partial` в документацию по каждому tool.

### Report Quality
- [x] Сделать `generate_audit_report` partial-aware.
- [x] Добавить status summary в Markdown report.
- [ ] Улучшить Markdown report до читаемого executive summary формата.
- [ ] Добавить рекомендации next actions в отчёт, а не только факты.
- [ ] Добавить явную маркировку skipped sections с причинами.
- [ ] Добавить machine-readable report export помимо Markdown.

### Dev Experience
- [x] Добавить `Makefile` с базовыми командами.
- [x] Улучшить `pyproject.toml` для сборки и metadata.
- [x] Обновить `CONTRIBUTING.md`.
- [ ] Добавить `README` раздел `Quickstart for MCP clients`.
- [ ] Добавить `troubleshooting` раздел для локального запуска.
- [ ] Добавить пример `.env` со всеми поддерживаемыми настройками runtime.

### CI / Packaging
- [x] Усилить GitHub Actions: test + lint + typecheck + build + smoke.
- [ ] Добавить release workflow.
- [ ] Добавить changelog policy.
- [ ] Добавить версионированные release notes.
- [ ] Добавить публикацию wheel/sdist artefacts в GitHub Releases.
- [ ] Добавить badge или статус для package build/release.

## Stage 2: Runtime Reliability

### HTTP / Resilience
- [ ] Добавить deterministic fallback для User-Agent, если `fake-useragent` недоступен.
- [ ] Переиспользовать один shared async HTTP client вместо создания клиента на каждый запрос.
- [ ] Уточнить retry policy по типам ошибок и статус-кодам.
- [ ] Добавить bounded concurrency для network-heavy tools.
- [ ] Добавить явные timeout categories для page fetch, sitemap fetch, external API.
- [ ] Добавить redirect re-validation для SSRF-safe поведения после редиректов.

### Error Handling / Observability
- [ ] Добавить структурированные логи для каждого tool invocation.
- [ ] Добавить debug mode через env/config.
- [ ] Добавить correlation/request id в логи и tool results при debug mode.
- [ ] Привести все провайдеры к одному набору error codes.
- [ ] Добавить partial-failure classification: timeout / provider_error / parse_error / unsupported.

### Testability
- [ ] Довести тесты до стабильного локального запуска из чистого `.venv`.
- [ ] Добавить smoke test, который импортирует `server.py` в CI без ручных допущений.
- [ ] Добавить coverage threshold по branch coverage, а не только line coverage.
- [ ] Добавить fixtures для redirect chains, malformed HTML, malformed XML, API rate limit.

## Stage 3: SEO Depth

### On-Page Audit
- [ ] Добавить проверки canonical consistency.
- [ ] Добавить проверки `noindex` / `nofollow` interpretation на уровне on-page.
- [ ] Добавить Open Graph / Twitter Card coverage.
- [ ] Добавить базовые hreflang checks.
- [ ] Добавить проверку title/description duplication heuristics.
- [ ] Добавить явные рекомендации по длине title/description и quality warnings.

### Technical Health
- [x] Добавить redirect и indexability signals.
- [x] Добавить canonical host check.
- [ ] Добавить www/non-www normalization check.
- [ ] Добавить trailing slash normalization check.
- [ ] Добавить robots.txt vs sitemap consistency checks.
- [ ] Добавить canonical-vs-redirect conflict detection.
- [ ] Добавить soft-404 style heuristics.

### Sitemap Audit
- [x] Добавить поддержку sitemap index.
- [x] Добавить partial reporting для failed pages.
- [ ] Добавить sampling strategies: first N / random / top-level balanced.
- [ ] Добавить per-page error reasons в results.
- [ ] Добавить concurrency limit для sitemap page scans.
- [ ] Добавить summary metrics по scanned pages quality score.

### Content Analysis
- [x] Добавить phrase-based target matching.
- [x] Добавить lexical diversity и bigrams.
- [ ] Убрать из описания любые упоминания TF-IDF, пока он реально не реализован.
- [ ] Добавить stopword filtering strategy.
- [ ] Добавить language-aware tokenization.
- [ ] Добавить section-level analysis по headings/body.
- [ ] Добавить basic content quality heuristics beyond density.

### Schema / Links / PSI
- [ ] Улучшить `check_schema_markup` для массивов, графов и нескольких JSON-LD блоков.
- [ ] Добавить классификацию schema issues по severity.
- [ ] Улучшить `check_broken_links_on_page` с различением broken / timeout / blocked.
- [ ] Добавить per-domain concurrency guard в broken links scan.
- [ ] Улучшить PSI output: source timestamps, field/lab distinction, clearer summaries.

## Stage 4: Ahrefs / External Provider Maturity

### Ahrefs Integration
- [x] Отметить нереализованные Ahrefs tools как `beta`.
- [ ] Решить судьбу `estimate_traffic`: реализовать или убрать из stable positioning.
- [ ] Решить судьбу `check_difficulty`: реализовать или убрать из stable positioning.
- [ ] Добавить единый adapter слой для всех Ahrefs responses.
- [ ] Добавить rate-limit handling и понятные provider-specific errors.
- [ ] Добавить integration tests на paid-provider failure modes.

### Provider Strategy
- [ ] Формально описать, какие external providers обязательны, а какие optional.
- [ ] Добавить capability matrix по env vars и доступным фичам.
- [ ] Подготовить расширяемую provider architecture для будущих data sources.

## Stage 5: Docs, Adoption, OSS Maturity

### Documentation
- [ ] Написать `Quickstart` для Cursor.
- [ ] Написать `Quickstart` для Claude Desktop.
- [ ] Написать `Quickstart` для Gemini CLI.
- [ ] Добавить примеры prompt flows для агентов.
- [ ] Добавить “when to use which tool” guide.
- [ ] Добавить FAQ по ограничениям и partial results.

### OSS Hygiene
- [ ] Добавить `SECURITY.md`.
- [ ] Добавить issue templates.
- [ ] Добавить pull request template.
- [ ] Добавить roadmap summary в README.
- [ ] Добавить public project board или milestones strategy.
- [ ] Подготовить first good issues / contributor-friendly backlog.

### Product Readiness
- [ ] Подготовить benchmark fixture pack для regression testing качества.
- [ ] Прогнать несколько реальных доменов и собрать sanity examples.
- [ ] Сравнить outputs с 1-2 зрелыми SEO tools и зафиксировать gaps.
- [ ] Определить критерии “v2.1 stable” и “v3.0 mature”.

## Progress Notes

- 2026-04-14: Введён единый response contract (`_meta`, structured `error`), улучшен `generate_audit_report`, усилены packaging/CI основы, углублены `technical_health_check`, `bulk_sitemap_audit`, `analyze_content_density`.
