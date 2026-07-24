# 产品需求规格说明书（PRD）

> **项目名称**：izone（TendCode 个人博客）
> **最后更新**：2026-06-25

---

## 1. 项目概述

izone 是一个基于 Django 框架搭建的个人博客系统，为博主提供文章发布、内容管理、读者互动等功能，同时集成在线工具、服务监控、导航网站等扩展模块。

**产品网址**：https://tendcode.com/

---

## 2. 目标用户

| 用户角色 | 说明 |
|---------|------|
| **博主（管理员）** | 通过 Django Admin 后台管理文章、友链、配置等所有内容 |
| **读者（访客）** | 浏览文章、搜索内容、发表评论、申请友链 |
| **注册用户** | 可通过 OAuth 登录，参与评论互动，接收通知 |

---

## 3. 核心功能

### 3.1 文章管理

- Markdown 写作，支持代码语法高亮（Pygments）
- 自定义 Markdown 扩展：删除线、图标、警告块、代码分组、Mermaid 图表
- 文章分类（Category）和标签（Tag）体系
- 专题-主题-文章（Subject → Topic → Article）层级组织结构
- 文章置顶、草稿/发布状态切换
- 文章封面图（django-imagekit 自动裁剪）
- SEO 优化：自定义 keywords、description、slug URL
- RSS 订阅（全站文章 Feed）
- Sitemap 网站地图自动生成

### 3.2 用户认证

- Django 自带用户系统 + 自定义 Ouser 模型（扩展头像字段）
- django-allauth 集成第三方登录（微博、GitHub）
- 邮箱注册/登录（用户名或邮箱均可登录）
- 登出直接退出免确认

### 3.3 评论系统

- 文章评论，支持二级回复（parent / rep_to 结构）
- Markdown 格式评论内容
- 微博表情支持（48 个 emoji 图标替换）
- 评论通知：被回复时创建 Notification，支持标记已读/删除
- 系统通知（SystemNotification）：平台级消息推送

### 3.4 全文搜索

- django-haystack + Whoosh 搜索引擎
- Jieba 中文分词（替换默认英文分析器）
- 实时索引更新（RealtimeSignalProcessor）
- 搜索结果高亮

### 3.5 数据统计

- 文章浏览量统计（30 分钟 session 去重 + 爬虫过滤）
- 单页面浏览量统计（可装饰器注入）
- 每日访问数据自动记录（ArticleView 模型 + 23:59 Celery 定时任务）
- 看板仪表盘（dashboard）：周/月访问趋势
- 热门文章排行（基于 Redis 缓存数据）

### 3.6 友链管理

- 友链展示页面（按创建时间排序）
- 在线申请友链（提交后等待管理员审核）
- Celery 定时自动校链：请求友链 URL，非 200 自动隐藏并记录原因
- 友链恢复：URL 恢复 200 后自动重新显示
- 支持校验友链是否回链本站

### 3.7 SEO 与站点服务

- robots.txt 动态生成
- Sitemap XML 自动生成（文章、分类、标签）
- 百度主动推送（Celery 定时任务 + URL 提交接口）
- 死链（Silian）管理页面
- 站长统计集成（友盟、51.la）

### 3.8 扩展模块

| 模块 | 说明 |
|------|------|
| 在线工具 | 条件启用（TOOL_FLAG），提供 IP 查询等实用工具 |
| 服务监控 | 服务器状态上报、在线/离线检测、邮件告警（MonitorServer 加密凭证） |
| 导航网站 | 工具网站推荐列表，自动校链，JSON API 接口 |
| 个人简历 | 在线简历展示 |
| 流程图服务 | 流程图绘制展示 |
| RSSHub | 第三方 RSS 源聚合展示（FeedHub 模型采集） |
| 健身看板 | 跑步数据记录与可视化（心率、配速、步频趋势） |
| 便签笔记 | 简短笔记卡片在首页展示 |
| 项目管理 | 个人项目展示列表 |
| 脚本分享 | 实用脚本工具集合，支持一键下载命令，Shell/Python 类型筛选 |
| 时间线 | 博客更新日志时间线 |

### 3.9 RESTful API

- 条件启用（API_FLAG）
- Django REST Framework 提供标准 REST 接口
- 涵盖：文章、标签、分类、用户、时间线、工具链接、导航网站
- 权限控制：BasicAuth + SessionAuth + IsAdminUser

### 3.10 异步任务

- Celery Worker + Celery Beat（基于 Redis 作为 Broker）
- 定时任务调度器：DatabaseScheduler（django-celery-beat）
- 核心定时任务：缓存更新、友链校验、通知清理、百度推送、每日访问统计、Feed 数据采集
- 动态脚本执行：支持存储 Python/Shell 脚本并通过 Celery 任务执行（TaskScript 模型）

---

## 4. 明确不做的边界

- ❌ 不涉及多用户博客平台（非 SaaS）
- ❌ 不涉及前台用户内容发布（仅管理员后台发布）
- ❌ 不涉及支付、电商功能
- ❌ 不涉及国际化多语言支持（目前仅中文）

---

## 5. 非功能需求

- **响应式设计**：Bootstrap 4，适配 PC / iPad / 手机
- **暗色主题**：支持深色模式切换
- **缓存策略**：Redis 缓存文章渲染结果（7 天）、热门数据、Feed 数据
- **性能**：标记渲染结果缓存，浏览量 session 去重
- **安全**：XSS 过滤（bleach）、评论内容清洗、CSRF 保护
- **可维护性**：Docker 部署，环境变量驱动配置

| — | 2026-07-24 | 根据 commit 2ca6b0b 更新：新增 3.8 脚本分享扩展模块 |
