# Skill 文章发布系统 - 设计文档

> 日期: 2026-07-16 | 状态: 待实现

## 1. 目标

开发一个 Claude Code Skill，让 AI 可以简单快速地发布文章到博客。支持从本地 markdown 文件或对话中直接输入内容，AI 自动解析、匹配已有分类/标签/主题，用户确认后一键发布。

## 2. 架构概览

```
用户提供 markdown 内容（文件/粘贴）
        │
        ▼
┌─────────────────────────────────┐
│  Claude Code Skill              │
│  (.claude/skills/publish.md)    │
│                                 │
│  1. 读取配置 (api_base, token)  │
│  2. 解析 markdown               │
│     - 提取标题 → 生成 slug       │
│     - 提取/生成摘要              │
│     - 分析内容 → 推断分类/标签   │
│  3. 调用 GET /skill/meta/       │
│     → 匹配已有分类/标签/主题     │
│  4. 展示推断结果，用户确认       │
│  5. 调用 POST /skill/articles/  │
│     publish/ 发布文章            │
└─────────────────────────────────┘
        │          ▲
        ▼          │
┌─────────────────────────────────┐
│  后端 API                        │
│  /openapi/v1/skill/             │
│                                 │
│  GET  /meta/    聚合查询        │
│  POST /articles/publish/  发布  │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  Django Models (已有)           │
│  Article, Category, Tag,        │
│  Topic, Subject, Keyword        │
└─────────────────────────────────┘
```

### 职责划分

| 层 | 做什么 | 不做什么 |
|----|--------|----------|
| **AI / Skill** | 理解文章内容、生成 slug、推断分类和标签、匹配已有数据、展示确认 | 不直接操作数据库 |
| **API** | 接收明确字段、按名称 get-or-create、校验必填项、返回清晰的中文错误 | 不做"智能推断"，不自动创建 topic |

## 3. 后端改动

### 3.1 全局 Token 认证

- 启用 `rest_framework.authtoken`（DRF 自带）
- 在 `settings.py` 的 `REST_FRAMEWORK` 默认认证类中加入 `TokenAuthentication`
- Token 在 Django Admin 中管理（关联到用户），供整套 REST API 使用
- 执行 `python manage.py migrate` 创建 Token 表

### 3.2 现有 API 权限调整

**`apps/api/views.py` — `ArticleListSet`：**
- `permission_classes` 从 `IsAdminUser` 改为 `IsAuthenticated`
- `authentication_classes` 加上 `TokenAuthentication`

其他 ViewSet（`TagListSet`、`CategoryListSet`）已有较宽松的权限，Token 认证通过全局配置生效即可。

### 3.3 Skill 专用接口

所有 skill 接口挂载在 `/openapi/v1/skill/` 下，独立于现有 REST API。

#### 3.3.1 聚合元数据查询

```
GET /openapi/v1/skill/meta/
```

**认证**: Token（Header: `Authorization: Token xxx`）

**响应 200:**
```json
{
  "categories": [
    { "id": 1, "name": "技术", "slug": "tech", "description": "技术文章" },
    { "id": 2, "name": "生活", "slug": "life", "description": "生活随笔" }
  ],
  "tags": [
    { "id": 1, "name": "Python", "slug": "python", "description": "Python编程" },
    { "id": 2, "name": "Django", "slug": "django", "description": "Django框架" }
  ],
  "topics": [
    {
      "id": 1,
      "name": "入门篇",
      "subject_id": 1,
      "subject_name": "Django实战系列",
      "subject_status": "ongoing"
    },
    {
      "id": 2,
      "name": "高级篇",
      "subject_id": 1,
      "subject_name": "Django实战系列",
      "subject_status": "ongoing"
    }
  ]
}
```

**实现**: 一个普通 DRF `APIView`，聚合查询 `Category`、`Tag`、`Topic`（select_related subject），返回结构化 JSON。仅 GET，只读。

#### 3.3.2 文章发布

```
POST /openapi/v1/skill/articles/publish/
```

**认证**: Token（Header: `Authorization: Token xxx`）

**字段约束（来自模型定义，AI 和接口共同遵守）：**

| 字段 | 模型定义 | Skill 行为 |
|------|----------|-----------|
| `title` | CharField, max_length=**150** | AI 保证 ≤150 字符 |
| `slug` | SlugField, max_length=**50**, **unique** | AI 根据标题生成，≤50 字符 |
| `body` | TextField（无限制） | 原始 markdown，不做修改 |
| `summary` | TextField, max_length=**230** | AI 根据文章内容生成，≤230 字符 |
| `is_publish` | BooleanField, default=True | **默认 `false`**（存草稿，手动发布时 create_date 自动更新） |
| `is_top` | BooleanField, default=False | AI 根据用户意图设置，默认 `false` |
| `img_link` | ProcessedImageField, blank=True, 有默认图 | **不传**，使用默认图片 |
| `category.name` | CharField, max_length=**20**（非 unique） | AI 匹配或生成，≤20 字符 |
| `category.slug` | SlugField, max_length=**50**, **unique** | AI 生成 |
| `category.description` | TextField, max_length=**240** | AI 生成，≤240 字符 |
| `tag.name` | CharField, max_length=**20**（非 unique） | AI 匹配或生成，≤20 字符 |
| `tag.slug` | SlugField, max_length=**50**, **unique** | AI 生成 |
| `tag.description` | TextField, max_length=**240** | AI 生成，≤240 字符 |
| `keyword.name` | CharField, max_length=**20** | AI 提取或生成 |
| `topic_order` | IntegerField, default=99, null/blank | 可选，默认 99 |
| `topic_short_title` | CharField, max_length=**50**, null/blank | 可选 |

> ⚠️ **注意**: Category 和 Tag 的 `name` 字段**不是 unique**，只有 `slug` 是 unique。接口按 name 查询时使用 `.filter(name=name).first()` 而非 `.get(name=name)`。

> **核心原则**:
> - 分类和标签的信息（name、slug、description）由 AI 补全，接口只做 get-or-create + 描述更新
> - `is_publish` 默认 `false`（存草稿），`img_link` 不传（使用默认图）
> - `Article.save()`: 当 `is_publish` 从 False→True 时，`create_date` 重置为发布时间
> - Category/Tag 按 `name` 查询使用 `.filter().first()`（name 非 unique，slug 才是 unique）

**入参:**
```json
{
  "title": "文章标题 ≤150字符（必填）",
  "slug": "ai-generated-slug ≤50字符（必填）",
  "body": "markdown 正文（必填）",
  "summary": "AI 据内容生成 ≤230字符（必填）",
  "is_publish": false,
  "is_top": false,
  "category": {
    "name": "分类名 ≤20字符（必填）",
    "slug": "分类slug ≤50字符（AI生成，必填）",
    "description": "SEO描述 ≤240字符（AI生成，必填）"
  },
  "tags": [
    {
      "name": "标签名 ≤20字符（必填）",
      "slug": "标签slug ≤50字符（AI生成，必填）",
      "description": "SEO描述 ≤240字符（AI生成，必填）"
    }
  ],
  "keywords": ["关键词 ≤20字符"],
  "topic": {
    "id": 1,
    "name": "主题名（可选，用于校验）"
  },
  "topic_order": 99,
  "topic_short_title": "简短标题 ≤50字符（可选）"
}
```

**接口内部逻辑:**

```
1. 校验必填字段: title, slug, body, category.name
2. 校验 slug 唯一性 → 冲突则返回错误
3. 处理 category（name 非 unique，使用 .filter().first() 查询）:
   - 按 name 查 → 存在 → 关联已有 Category
     - 同时检查 description: 如果 AI 提供了更好的描述 → 更新
   - 不存在 → 用 AI 提供的 slug + description 创建新 Category
   - slug 冲突 → 返回错误
4. 处理 tags（逐个，name 非 unique，使用 .filter().first() 查询）:
   - 按 name 查 → 存在 → 关联已有 Tag
     - 同时检查 description: 如果 AI 提供了更好的描述 → 更新
   - 不存在 → 用 AI 提供的 slug + description 创建新 Tag
   - slug 冲突 → 返回错误
5. 处理 keywords（逐个）:
   - 按 name get-or-create
6. 处理 topic:
   - 如果提供了 topic.id → 直接查 ID 关联
   - 如果提供了 topic.name → 按名称查，找到关联
   - 都不存在 → 不创建，返回错误，列出可用主题
7. 从 request.user 设置 author
8. 设置 is_top（默认 false）
9. 设置 is_publish = False（存草稿，发布时 save() 自动更新 create_date）
10. 创建 Article，返回成功结果
```

**成功响应 201:**
```json
{
  "success": true,
  "id": 42,
  "url": "/article/django-rest-framework-best-practices/",
  "title": "Django REST Framework 最佳实践"
}
```

**错误响应 400 — 清晰的中文描述:**
```json
{"success": false, "error": "标题不能为空"}
{"success": false, "error": "slug 'hello-world' 已被文章 'Hello World' 使用，请更换"}
{"success": false, "error": "分类 'Python' 不存在，尝试创建时 slug 'python' 已被分类 'Python进阶' 占用"}
{"success": false, "error": "标签 'AI' 不存在，尝试创建时 slug 'ai' 已被标签 '人工智能' 占用"}
{"success": false, "error": "主题 '不存在的主题' 不存在，可用主题: 入门篇、高级篇、实战篇"}
{"success": false, "error": "请求格式错误: category.name 为必填项"}
```

### 3.4 需要新增/修改的文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `izone/settings.py` | 修改 | 加 `rest_framework.authtoken`，配置 `TokenAuthentication` |
| `apps/api/views.py` | 修改 | 改 ArticleListSet 权限；新增 SkillMetaView、SkillPublishView |
| `apps/api/serializers.py` | 修改 | 新增 `ArticlePublishSerializer`、`TopicListSerializer` |
| `apps/api/urls.py` | 修改 | 新增 skill 专用路由 |

## 4. Skill 设计

### 4.1 配置文件

路径: `.claude/skill-publish.json`

```json
{
  "api_base": "https://your-domain.com/openapi/v1",
  "token": "your-auth-token-here",
  "default_category": {
    "name": "技术",
    "slug": "tech",
    "description": "技术相关文章"
  },
  "preferred_tags": [
    { "name": "Python", "slug": "python", "description": "Python编程语言" },
    { "name": "Django", "slug": "django", "description": "Django框架" }
  ]
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `api_base` | 是 | 博客 API 地址，不含尾部斜杠 |
| `token` | 是 | 认证 Token，在 Django Admin 中为用户创建 |
| `default_category` | 否 | 默认分类，skill 优先使用此项 |
| `preferred_tags` | 否 | 常用标签库，AI 优先匹配，未匹配到的建议新建 |

### 4.2 Skill 指令文件

路径: `.claude/skills/publish-article.md`

Skill 指令的核心内容（告诉 AI 如何执行发布流程）：

1. **读取配置**: 从 `.claude/skill-publish.json` 获取 api_base、token、默认分类等
2. **获取内容**: 用户提供 markdown 文件路径或直接粘贴内容
3. **解析内容**（遵守字段约束表）:
   - 从第一个 `# 标题` 提取 title，保证 ≤150 字符
   - 生成 slug: 英文翻译/音译，小写，空格转连字符，≤50 字符
   - 生成 summary: 根据文章内容总结提炼，非简单截取，≤230 字符
   - 分析关键词，推断分类和标签
   - 分类/标签信息补全: name（≤20）、slug（≤50）、description（≤240）
   - `is_publish` 默认 `false`（存草稿，后续手动发布时 create_date 自动更新）
   - `is_top` 默认 `false`
   - `img_link` 不传（使用默认图片）
4. **查询上下文**: `GET {api_base}/skill/meta/` 获取已有分类/标签/主题
5. **匹配决策**:
   - 分类: 配置默认 > 内容推断 > 询问用户
   - 标签: 名称精确匹配已有标签 > 名称模糊匹配 > 建议新建
   - 主题: 匹配已有主题 > 不设置
   - 对于已匹配到的分类/标签：复用已有信息，如果原描述缺失或不清晰，AI 生成更好的描述传入（接口会更新）
   - 对于新建的分类/标签：AI 生成完整的 name、slug、description
6. **展示确认**: 一次性展示所有解析结果，等待用户确认或微调
7. **发布**: `POST {api_base}/skill/articles/publish/`
8. **错误处理**: 解析错误信息，自动修复可修复的（如 slug 冲突→重新生成），无法修复的展示给用户
9. **报告结果**: 成功则展示文章链接

### 4.3 交互示例

```
用户: 发布 ~/articles/drf-best-practices.md

AI:
  我解析了这篇文章，请确认以下信息：

  📝 标题: 《Django REST Framework 最佳实践》 (28字符)
  🔗 Slug: drf-best-practices
  📂 分类: 技术（已有）
  🏷️ 标签: Django（已有）, REST API（新建）, Python（已有）
  📖 主题: Django实战系列 → 入门篇（连载中）
  📌 置顶: 否
  📄 摘要: 本文介绍了 DRF 开发中的 10 个最佳实践，包括序列化器设计、
         权限控制、性能优化等方面... (87字符)
  📝 状态: 存为草稿（需在后台手动发布）

  确认提交吗？或告诉我要调整的地方。

用户: 标签加个 DRF

AI:
  ✅ 文章已保存为草稿！
  预览地址: https://izone.org.cn/article/drf-best-practices/
  可在后台设置发布状态。
```

## 5. 实现计划（概要）

### Phase 1: 后端 API
1. 配置 Token 认证（settings + migrate）
2. 创建 SkillMetaView（`GET /skill/meta/`）
3. 创建 SkillPublishSerializer
4. 创建 SkillPublishView（`POST /skill/articles/publish/`）
5. 调整现有 ArticleListSet 权限
6. 配置 URL 路由
7. 手动测试 API（curl）

### Phase 2: Skill 文件
1. 编写 `.claude/skills/publish-article.md` 指令文件
2. 引导创建 `.claude/skill-publish.json` 配置文件
3. 端到端测试

### Phase 3: 文档
1. 更新 CLAUDE.md 添加 skill 使用说明
2. 为 Admin Token 管理写简短说明

## 6. 设计决策记录

| 决策 | 选项 | 选择 | 原因 |
|------|------|------|------|
| 认证方式 | Token / API Key / 仅 Session | **Token** | DRF 自带，Admin 可管理，全局复用 |
| 聚合查询 | 多个接口 / 一个聚合接口 | **一个聚合接口** | 减少 AI 的 HTTP 往返，一次性拿到所有上下文 |
| 接口路径 | 复用现有 REST API / 独立 /skill/ 前缀 | **独立 /skill/ 前缀** | 与现有 REST API 物理隔离，职责清晰 |
| 分类/标签匹配 | 按 ID / 按 name | **按 name** | name 非 unique 但实际不会重复；接口用 .filter().first() |
| 分类/标签创建 | 接口只查不建 / get-or-create + 描述更新 | **get-or-create + 更新** | AI 提供完整信息，已有则更新描述，新则创建 |
| 主题处理 | 允许自动创建 / 仅查不允许建 | **仅查询不允许创建** | 主题有层级关系（Subject→Topic），自动创建风险高 |
| Slug 生成 | 后端用 pypinyin / AI 生成 | **AI 生成** | AI 擅长语义理解和翻译，无需引入额外依赖 |
| 内容解析 | 后端解析 / AI 解析 | **AI 解析** | AI 天然理解 markdown 结构和语义 |
| is_publish | 默认 true / 默认 false | **默认 false（草稿）** | 利用 save() 行为：发布时 create_date 自动更新为发布时间 |
