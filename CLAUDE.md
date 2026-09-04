# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Virtual environment
source /Users/leizhu/Documents/Private/MyDemos/env/bin/activate

# Database
python manage.py migrate
python manage.py makemigrations

# Run development server
python manage.py runserver

# Rebuild search index (after article changes)
python manage.py rebuild_index

# Clear Django cache
python manage.py clear_cache

# Compile translation messages (for i18n)
django-admin compilemessages

# Start Celery worker (for async tasks)
celery -A izone worker -l info

# Start Celery beat (for scheduled tasks)
celery -A izone beat -l info

# Run a specific Celery task via shell
python manage.py shell
```

## Architecture Overview

**Stack**: Django 2.2 + Python 3.9 + MySQL + Redis + Celery + Bootstrap 4

**Project layout**: `izone/` holds Django project settings/urls/wsgi. `apps/` contains all Django apps (added to `sys.path` in settings). `templates/` holds shared templates. `utils/` holds shared utilities like custom markdown extensions.

### Core Apps

- **`blog`** — The main app: `Article`, `Category`, `Tag`, `Subject`/`Topic` (hierarchical: Subject → Topic → Article), `Timeline`, `Carousel`, `FriendLink`, `AboutBlog`, `PageView`, `ArticleView` (daily stats), `FeedHub` (RSS aggregation), `MenuLink`, `SiteConfig` (JSON-based site config), `Fitness`, `Project`, `Note`. Views use Django class-based views heavily (ListView, DetailView). Article slug is the URL identifier.
- **`oauth`** — Custom user model `Ouser` (extends `AbstractUser`) with avatar field via django-imagekit. django-allauth handles social auth (Weibo, GitHub).
- **`comment`** — `ArticleComment` model with parent/reply-to for threaded comments. `Notification` for comment replies, `SystemNotification` for platform notices. Emoji replacement from Weibo emoji set.
- **`easytask`** — Celery `@shared_task` definitions in `tasks.py`, with actual logic extracted to `actions.py` and `action/` subpackage. Also holds `TaskScript` and `EnvironmentVariable` models for dynamic script execution.
- **`tool`**, **`api`** — Conditionally loaded apps (controlled by `TOOL_FLAG` and `API_FLAG` env vars). `api` provides RESTful endpoints via Django REST Framework `ModelViewSet`s.
- **`monitor`** — Server monitoring with encrypted client credentials (`MonitorServer` model).
- Other apps: `webstack` (navigation), `resume`, `portinfo`, `flow`, `rsshub`.

### URL Routing

Defined in [izone/urls.py](izone/urls.py). Root paths: `/` (blog index), `/article/<slug>/` (article detail), `/category/<slug>/`, `/tag/<slug>/`, `/subject/`, `/search/`, `/friend/`, `/about/`, `/timeline/`, `/archive/`, `/comment/`, `/accounts/` (auth), `/nav/`, `/rss/`, `/monitor/`, `/resume/`, `/tool/` (conditional), `/openapi/v1/` (conditional, API).

### Article Content Pipeline

1. Articles stored as raw Markdown in `Article.body`
2. On view, rendered via `markdown` library with custom extensions in [utils/markdown_ext.py](utils/markdown_ext.py): `DelExtension` (~~text~~), `IconExtension` (icon:xxx), `AlertExtension` (::: primary/warning/danger blocks), `CodeGroupExtension` / `CodeItemExtension` (tabbed code blocks)
3. Mermaid blocks (` ```mermaid`) are preprocessed to `<pre class="mermaid">` before markdown conversion
4. Code highlighting via Pygments with `CustomHtmlFormatter`
5. Rendered HTML is cached in Redis for 7 days, keyed by `article:markdown:<id>:<update_timestamp>`

### Search

Search uses MySQL FULLTEXT with the n-gram parser (migration `blog.0027_article_fulltext_index` adds a FULLTEXT index on `title, body, summary`). The search view `MySearchView` (apps/blog/views.py) runs `MATCH ... AGAINST (IN BOOLEAN MODE)` plus a per-word substring filter for precision. No separate search index to build or keep in sync.

### Cache Strategy

django-redis with Redis as backend. Key patterns defined in `blog.utils.RedisKeys`. Cached content: article rendered markdown, hot article lists, weekly/daily view statistics, feed hub data, health dashboard data. `blog.context_processors.settings_info` provides global template context from `SiteConfig` model (or falls back to Django settings env vars).

### Page View Tracking

`blog.utils.add_views` decorator (for named URL pages) and `BaseDetailView.get_object` (for articles) track views with:
- User-Agent filtering (blocks bots/spiders/curl via `check_request_headers`)
- 30-minute session-based deduplication
- Admin/author self-views excluded
- Daily stats written to `ArticleView` model by a nightly Celery task

### Celery Tasks (defined in [easytask/tasks.py](apps/easytask/tasks.py))

- `update_cache` — rebuilds article markdown cache and blog statistics
- `check_friend` — validates friend link sites are reachable
- `clear_notification` — removes old notifications
- `set_views_to_redis` — writes daily view stats (run at 23:59)
- `baidu_push` — SEO URL submission to Baidu
- `qiniu_sync_github` / `article_to_github` — sync ops
- `execute_task` — dynamic execution of stored Python/Shell scripts from `TaskScript` model

### Deployment

Docker-based: `entrypoint.sh` runs migrations + collectstatic, then starts supervisord which manages `gunicorn` (Django WSGI on port 8000), `celery-worker`, and `celery-beat`. Two Dockerfiles: standard (`Dockerfile`) and slim (`Dockerfile-slim`) variants. All config is env-var driven (MySQL host/credentials, Redis host, email, site metadata, feature flags).

### Key Patterns

- **Site config**: `SiteConfig` model (singleton, enforced in `save()`) stores site metadata as JSON, read by `blog.context_processors.settings_info`. Falls back to `settings.py` env vars.
- **Subject/Topic structure**: `Subject` → `Topic` → `Article`. Articles with a `topic` use subject-specific URLs. Articles without topic are "standalone".
- **Template tags**: [blog/templatetags/blog_tags.py](apps/blog/templatetags/blog_tags.py) provides `get_article_list`, `get_category_list`, `get_tag_list`, `load_pages` (custom pagination), `get_feed_list`, `get_blog_infos`, etc.
- **Signals**: `blog/signals.py` and `comment/signals.py` likely handle search index updates and notification creation on comment save.
- **Admin customizations**: Each app has its own `admin.py` for Django admin registration.

## Skill: 发布文章 (publish-article)

通过 AI 对话快速发布文章到博客。

**配置**: 设置环境变量 `IZONE_API_TOKEN`（在 `/adminx/authtoken/token/` 获取）和 `IZONE_API_BASE`。

**API 端点**:
- `GET  /openapi/v1/skill/meta/` — 聚合查询分类、标签、主题（需 Token 认证）
- `POST /openapi/v1/skill/articles/publish/` — 发布文章（需 Token 认证）

**使用方式**:
- `发布文章 /path/to/article.md` — 从本地 markdown 文件发布
- `发布文章` 然后粘贴内容 — 从对话中输入

**工作流程**: AI 解析 markdown → 查询已有分类/标签/主题 → 匹配并展示预览 → 用户确认 → 发布（默认存为草稿）

**认证**: 所有 skill API 使用 `Authorization: Token <token>` 请求头认证。Token 在 Admin 中创建，关联到用户。

**环境要求**: 需要设置 `IZONE_API_FLAG=True` 环境变量以启用 API 路由。
