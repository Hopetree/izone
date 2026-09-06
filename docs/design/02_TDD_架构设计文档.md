# 架构设计文档（TDD）

> **项目名称**：izone（TendCode 个人博客）
> **最后更新**：2026-06-25

---

## 1. 技术栈

| 层级 | 技术选型 | 版本 |
|------|---------|------|
| 语言 | Python | 3.9 |
| Web 框架 | Django | 2.2.28 |
| 数据库 | MySQL（utf8mb4） | - |
| 缓存 | Redis（django-redis） | 4.10 |
| 消息队列 | Redis（Celery Broker） | - |
| 异步任务 | Celery + django-celery-beat + django-celery-results（Worker 与 Beat 合并单进程） | 4.4 |
| 搜索引擎 | MySQL FULLTEXT（n-gram 中文分词，随数据实时更新） | 5.7 |
| Web 服务器 | Gunicorn + supervisord | 19.9 / 4.2 |
| 容器化 | Docker | - |
| 前端 | Bootstrap 4 + jQuery | - |
| 后台 UI | bootstrap-admin | 0.4.3 |
| 第三方认证 | django-allauth（微博、GitHub） | 0.42 |
| REST API | Django REST Framework | 3.11 |
| 图片处理 | django-imagekit + Pillow | 4.0 / 9.3 |
| Markdown | Python-Markdown + Pygments + bleach | 3.4 / 2.15 |
| 表单 | django-crispy-forms | 1.7 |

---

## 2. 项目结构

```
izone/
├── izone/                     # Django 项目配置目录
│   ├── settings.py            # 全部配置集中（数据库/缓存/Celery/邮件/日志等）
│   ├── urls.py                # 根路由分发
│   └── wsgi.py                # WSGI 入口
│
├── apps/                      # 所有 Django 应用（sys.path 注入）
│   ├── blog/                  # ★ 核心博客应用
│   │   ├── models.py          # 所有数据模型（20+ 模型）
│   │   ├── views.py           # 视图（CBV 为主）
│   │   ├── urls.py            # 路由
│   │   ├── admin.py           # 后台注册
│   │   ├── context_processors.py # 全局模板上下文（含静态文件版本号管理）
│   │   ├── utils.py           # 工具函数（浏览量装饰器、RedisKeys、API 响应类等）
│   │   ├── task_views.py      # Celery 任务手动触发视图
│   │   ├── feeds.py           # RSS Feed
│   │   ├── sitemaps.py        # Sitemap
│   │   ├── signals.py         # Django 信号处理
│   │   ├── templatetags/      # 模板标签（blog_tags.py / dashboard.py / health.py）
│   │   ├── static/            # 静态资源（CSS/JS/img）
│   │   └── templates/blog/    # 模板文件
│   │
│   ├── oauth/                 # 自定义用户应用
│   │   └── models.py          # Ouser（AbstractUser 扩展）
│   │
│   ├── comment/               # 评论应用
│   │   ├── models.py          # ArticleComment / Notification / SystemNotification
│   │   └── views.py           # 评论添加/通知查看/标记已读
│   │
│   ├── easytask/              # 异步任务应用
│   │   ├── tasks.py           # @shared_task 任务定义
│   │   ├── actions.py         # 任务执行逻辑（友链校验/百度推送/统计数据等）
│   │   ├── models.py          # TaskScript / EnvironmentVariable
│   │   └── action/            # 按功能拆分的 action 模块
│   │       ├── friend_links.py
│   │       ├── article_sync.py
│   │       ├── oss_sync.py
│   │       └── clear_redis_keys.py
│   │
│   ├── api/                   # RESTful API（条件启用）
│   │   ├── views.py           # DRF ModelViewSet
│   │   ├── serializers.py     # 序列化器
│   │   └── urls.py            # DRF Router
│   │
│   ├── tool/                  # 在线工具（条件启用）
│   ├── monitor/               # 服务器监控
│   ├── webstack/              # 导航网站
│   ├── resume/                # 个人简历
│   ├── portinfo/              # 端口信息
│   ├── flow/                  # 流程图服务
│   ├── scripts/               # 脚本分享（公开下载 + 一键命令）
│   └── rsshub/                # RSSHub 订阅
│
├── templates/                 # 共享模板
│   ├── account/               # 认证相关模板
│   ├── admin/                 # 后台模板
│   └── search/                # 搜索结果模板
│
├── utils/                     # 项目级共享工具
│   └── markdown_ext.py        # 自定义 Markdown 扩展
│
├── media/                     # 用户上传媒体文件
├── static/                    # collectstatic 收集目录
├── locale/                    # 国际化翻译文件
├── log/                       # 日志文件目录
│
├── manage.py                  # Django 管理入口
├── requirements.txt           # Python 依赖
├── Dockerfile                 # Docker 标准镜像
├── Dockerfile-slim            # Docker slim 镜像（含编译依赖）
├── entrypoint.sh              # 容器入口（migrate + collectstatic → supervisord）
└── supervisord.conf           # 进程管理配置（含日志轮转 20MB×5）
```

---

## 3. 模块架构与数据流

### 3.1 请求处理流程

```
用户浏览器
    │
    ▼
Nginx (反向代理)
    │
    ▼
Gunicorn (WSGI)
    │
    ▼
Django (izone/wsgi.py → urls.py → app views)
    │
    ├── 模板渲染 ← context_processors (全局上下文)
    │        │
    │        └── SiteConfig 模型 → 全局配置
    │
    ├── Redis 缓存
    │   ├── 文章 Markdown 渲染结果（7天过期）
    │   ├── 热门文章 / 工具排行
    │   └── 统计图表数据
    │
    ├── MySQL 数据库
    │   ├── 文章 / 分类 / 标签 / 专题
    │   ├── 用户 / 评论 / 通知
    │   ├── 友链 / 导航 / 监控 / 脚本
    │   └── Celery 任务结果
    │
    └── MySQL FULLTEXT 全文索引
        └── blog_article(title, body, summary) WITH PARSER n-gram，随数据实时更新
```

### 3.2 异步任务架构

```
Celery Beat (DatabaseScheduler)
    │
    ├── update_cache           → 定时刷新文章 Markdown 缓存
    ├── check_friend           → 友链有效性校验
    ├── clear_notification     → 过期通知清理
    ├── set_views_to_redis     → 每日 23:59 写入访问统计
    ├── baidu_push             → 百度 SEO URL 推送
    ├── set_feed_data          → RSS Feed 数据采集
    ├── check_navigation_site  → 导航网站校验
    ├── clear_expired_sessions → 过期 Session 清理
    └── check_host_status      → 服务监控节点状态检查

Celery Worker（与 Beat 合并单进程：celery worker -B --pool=solo，Beat 以子进程运行）
    │
    └── Redis Broker (db 1) → 消费任务
    └── 结果存储：django-db（MySQL）
```

### 3.3 文章内容渲染管道

```
Article.body (原始 Markdown)
    │
    ├── 1. preprocess_mermaid_blocks()
    │      └── 将 ```mermaid 代码块转为 <pre class="mermaid">
    │
    ├── 2. Python-Markdown 渲染
    │      ├── extensions.extra (表格/代码块/属性列表)
    │      ├── markdown_checklist (任务列表)
    │      ├── CodeHiliteExtension + CustomHtmlFormatter (代码语法高亮)
    │      ├── TocExtension (自动生成目录锚点)
    │      ├── DelExtension (~~删除线~~)
    │      ├── IconExtension (icon:xxx → Font Awesome 图标)
    │      ├── AlertExtension (::: primary/warning/danger → Bootstrap Alert)
    │      ├── CodeItemExtension / CodeGroupExtension (代码分组 Tabs)
    │      └── mermaid (前端的 Mermaid.js 渲染)
    │
    ├── 3. 渲染结果缓存到 Redis
    │      └── Key: article:markdown:<id>:<update_timestamp> (TTL 7天)
    │
    └── 4. 模板中输出 HTML
```

---

## 4. 部署架构

```
┌─────────────────────────────────────────┐
│              Docker Container            │
│  ┌─────────────────────────────────┐    │
│  │        entrypoint.sh             │    │
│  │  python manage.py migrate        │    │
│  │  python manage.py collectstatic  │    │
│  └──────────────┬──────────────────┘    │
│                 ▼                        │
│  ┌────────── supervisord ──────────┐    │
│  │  ┌───────────────────────────┐  │    │
│  │  │ Gunicorn :8000            │  │    │
│  │  │ --workers 1 --max-requests│  │    │
│  │  └───────────────────────────┘  │    │
│  │  ┌───────────────────────────┐  │    │
│  │  │ Celery (worker -B solo)   │  │    │
│  │  │ 异步执行+定时调度单进程      │  │    │
│  │  └───────────────────────────┘  │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘
          │              │
          ▼              ▼
    ┌─────────┐   ┌─────────┐
    │  MySQL  │   │  Redis  │
    │  :3306  │   │  :6379  │
    └─────────┘   └─────────┘
```

**构建镜像**：
```bash
# 标准镜像
docker build -t hopetree/izone:lts .

# Slim 镜像（国内构建使用镜像源加速）
docker build --build-arg pip_index_url=http://mirrors.aliyun.com/pypi/simple/ \
             --build-arg pip_trusted_host=mirrors.aliyun.com \
             --build-arg debian_host=mirrors.ustc.edu.cn \
             -f Dockerfile-slim -t hopetree/izone:lts .
```

---

## 5. 环境变量配置

所有运行环境配置均通过环境变量注入，关键变量：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `IZONE_DEBUG` | 调试模式 | `True` |
| `IZONE_SECRET_KEY` | Django SECRET_KEY | 内置默认值 |
| `IZONE_MYSQL_HOST` | MySQL 主机 | `127.0.0.1` |
| `IZONE_MYSQL_NAME` | 数据库名 | `izone` |
| `IZONE_MYSQL_USER` | 数据库用户 | `root` |
| `IZONE_MYSQL_PASSWORD` | 数据库密码 | `python` |
| `IZONE_MYSQL_PORT` | 数据库端口 | `3306` |
| `IZONE_REDIS_HOST` | Redis 主机 | `127.0.0.1` |
| `IZONE_REDIS_PORT` | Redis 端口 | `6379` |
| `IZONE_TOOL_FLAG` | 启用在线工具模块 | `True` |
| `IZONE_API_FLAG` | 启用 REST API 模块 | `False` |
| `IZONE_LOGO_NAME` | 网站 Logo 名称 | `TendCode` |
| `IZONE_SITE_DESCRIPTION` | 网站描述 | 内置文本 |
| `IZONE_SITE_KEYWORDS` | 网站关键词 | 内置文本 |
| `IZONE_EMAIL_*` | 邮件服务器配置 | 163 SMTP 默认值 |
| `IZONE_PROTOCOL_HTTPS` | HTTP/HTTPS 协议 | `HTTP` |

| — | 2026-07-24 | 根据 commit 2ca6b0b 更新：项目结构新增 scripts 应用，请求处理流程新增脚本数据 |
| — | 2026-09-05 | 根据 commit f7b1c7e 更新：搜索引擎切换为 MySQL FULLTEXT(n-gram)，移除 haystack/Whoosh；Celery Worker 与 Beat 合并单进程；supervisord 日志轮转；删除 whoosh_index 相关内容 |
