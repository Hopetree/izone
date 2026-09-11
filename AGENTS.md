# AGENTS.md

> izone 博客项目的代理工作指南。**只包含项目本身的内容**；运维/环境信息（服务器地址、SSH 访问、部署命令、本地路径、密钥、端口等）属于敏感信息，只存放在本地持久记忆里，**禁止写入本文件**。

## 项目概览

izone 是一个基于 **Django 2.2 + Bootstrap 4** 的个人博客站点，除博客外还包含评论、站内搜索、在线工具、REST API（DRF）、服务监控、脚本分享平台等（`apps/` 下 12 个 app）。生产以 Docker 部署（见 `Dockerfile` / `Dockerfile-slim`）。

## 技术栈与版本（整体偏老，升级是已知计划）

- Python 3.9 / Django 2.2.28（已 EOL）/ MySQL 5.7 / Redis / Celery 4.4.2 / gunicorn 19.9
- **不要顺手做大版本升级**；升级（尤其 Django）是独立的 P2 计划，需要单独排期。
- `requirements.txt` 已移除 `django-haystack`、`Whoosh`；`jieba` 保留（词云工具用，已改为函数内延迟导入）。

## 本地开发

- 依赖：`pip install -r requirements.txt`
- 数据库与缓存连接走 `izone/settings.py` 的环境变量默认值（MySQL + Redis），本地按默认配置即可运行，无需额外环境变量
- 常用命令：
  - `python manage.py runserver`
  - `python manage.py migrate` / `makemigrations`
  - `python manage.py clear_cache`（清 Django 缓存）
  - `django-admin compilemessages`（编译 locale 翻译）
  - `celery -A izone worker -l info -B --pool=solo`（本地起 Celery，worker 与 beat 一体，与生产一致）
- **搜索无需构建索引**：已切换到 MySQL FULLTEXT，直接查询活库（旧的 `rebuild_index` 命令已随 haystack 移除）。

## 架构

### 目录结构

- `izone/`：Django 项目（settings/urls/wsgi）
- `apps/`：全部业务 app（`sys.path` 已注入，import 用 `from blog.models import ...` 形式）
- `templates/`：共享模板；`utils/`：自定义 markdown 扩展等
- `apps/blog` 是主 app：Article（slug 作为 URL 标识）、Category、Tag、Subject/Topic（层级）、Timeline、Carousel、FriendLink、FeedHub（RSS 聚合）、SiteConfig（JSON 站点配置）、Project、Note 等，视图以 CBV（ListView/DetailView）为主。

### 文章渲染管线

1. 正文存原始 Markdown（`Article.body`）
2. 视图渲染时用 `markdown` 库 + 自定义扩展（`utils/markdown_ext.py`：删除线/图标/提示块/代码组），Pygments 高亮
3. 渲染结果进 Redis 缓存 7 天（key：`article:markdown:<id>:<update_timestamp>`）

### 搜索（2026-09-05 重构）

- MySQL FULLTEXT + n-gram 解析器，索引 `blog_article(title, body, summary)`（迁移 `blog.0027_article_fulltext_index`）
- 视图 `apps/blog/views.py::MySearchView`：`MATCH ... AGAINST (IN BOOLEAN MODE)` + 每个词做 `icontains` 子串过滤保精度；查询前用正则剥离 BOOLEAN MODE 操作符
- 模板 `templates/search/blog/search.html` 用自定义标签 `my_snippet`（`blog_tags.py`）做截词高亮

### 缓存与统计

- django-redis（`blog.utils.RedisKeys` 定义 key 模式，全局 `KEY_PREFIX=izone`，`IGNORE_EXCEPTIONS` 让 Redis 抖动时静默降级）；`blog.context_processors.settings_info` 提供全局模板上下文
- 缓存对象：文章 Markdown（7 天）、RSS feed 正文（7 天，独立 key）、站点配置（1 小时）、侧边栏统计/标签/分类/菜单（1 小时）、未读通知计数（60 秒）
- 缓存失效：`blog/signals.py` 按模型精确失效（Article 全清、Tag/Category/MenuLink/ArticleComment 只清各自影响的 key；Article 仅 `views` 变化时跳过）
- 访问量统计：`blog.utils.add_views` 装饰器与文章详情页均用 Redis `cache.add` 做 **30 分钟按访客去重**（key 里必须带 `session_key`，缺访客维度会退化成全站每 URL 只计 1 次）+ UA 黑名单过滤，作者与超管不计数；每日统计由 Celery 夜间任务写入 `ArticleView`
- **Session 用 `cached_db`（读 Redis、写 Redis+MySQL）**，`CONN_MAX_AGE=60` 复用数据库连接；匿名访客首次计数访问会创建 session，依赖定时任务 `clear_expired_sessions` 清理

### Celery（2026-09-05 优化后，2026-09-11 补充配置）

- **worker 与 beat 合并为单进程**：`celery -A izone worker -l info -B --pool=solo`（Celery 4.4 的嵌入式 beat 会作为子进程，实际是 supervisord + gunicorn master/worker + celery 共 4 个 Python 进程）
- 关键配置（`izone/settings.py`）：`prefetch_multiplier=1`；**`CELERY_TASK_ACKS_LATE=False`（默认收到即 ack，脚本执行/推送等非幂等任务重复执行代价高于丢失），仅 `update_cache` 显式 `acks_late=True`**；`result_expires=1 天`；`visibility_timeout=12 小时`
- 任务定义在 `apps/easytask/tasks.py`：缓存刷新、友链检查、通知清理、百度推送、日访问量统计、feed 采集、session 清理、主机监控、动态脚本执行等
- 任务实现注意：外呼一律带超时（feed 8s、友链/导航 5s）；批量校验用有界并发（友链 semaphore、导航 8 线程且线程内 `connection.close()`）；`execute_task` 有 300s 硬超时与 100KB 输出截断，只继承 PATH/HOME/LANG/TZ
- 定时调度用 `django_celery_beat` DatabaseScheduler（admin 里管理），admin 还有「运行任务」页面（`blog/task_views.py`，`send_task` 动态执行）

### 关键模式

- SiteConfig 单例（save 时强约束）存站点 JSON 配置，由上下文处理器读取
- 大量模板标签在 `blog/templatetags/blog_tags.py`（列表/分类/分页 `load_pages` 等）
- signals 处理评论通知
- 功能开关：`TOOL_FLAG`、`API_FLAG` 环境变量控制 tool/api 两个 app 的路由

## 构建与部署约束（仅项目层面）

- `supervisord.conf` 在 Dockerfile 中 `COPY` 进镜像：**改进程配置（gunicorn/celery 启动参数）= 改仓库文件 → 重新构建镜像 → 重启容器**，无法在运行中的容器里持久修改
- gunicorn 固定 `--workers 1 --max-requests 1000 --max-requests-jitter 100`（2C2G 上防内存增长）
- 生产 compose 不在本仓库，在服务器上独立维护；**服务器地址、SSH、部署命令等运维细节见本地记忆，勿写入本文件**
- 遗留优化：Dockerfile 多阶段构建瘦身、INSTALLED_APPS 裁剪（需确认未用功能）、Django/celery/gunicorn 版本升级

## Git 工作流

- 主分支 `latest`；仓库有两个 remote（origin 为部署构建源）
- **改完代码默认只保留在本地：不要主动 push 到远程，更不要主动部署生产。推送和部署只在用户明确要求时执行。**
- commit message 遵循 conventional 格式 + 中文描述，如 `feat(blog): ...`、`fix(scripts): ...`、`perf(deploy): ...`、`chore(search): ...`

## 内容发布（技能）

- **发布文章**：设置 `IZONE_API_TOKEN`（在 `/adminx/authtoken/token/` 获取）与 `IZONE_API_BASE`；接口 `GET /openapi/v1/skill/meta/`（分类/标签/主题，Token 认证）、`POST /openapi/v1/skill/articles/publish/`；需 `IZONE_API_FLAG=True` 启用 API 路由
- **脚本分享平台**：`apps/scripts` 提供脚本发布能力（izone-publish-script skill），同样走 Token 认证