# API Reference

## Endpoints

Base URL: `$IZONE_API_BASE` (e.g. `http://127.0.0.1:8000/openapi/v1`)

### GET /skill/meta/

Returns all existing categories, tags, and topics for matching.

**Auth:** `Authorization: Token <token>`

**Response 200:**

```json
{
  "categories": [
    { "id": 1, "name": "Python Web开发", "slug": "Python-Web-development", "description": "..." },
    { "id": 2, "name": "Linux 笔记", "slug": "linux-notes", "description": "..." }
  ],
  "tags": [
    { "id": 1, "name": "Python", "slug": "python", "description": "..." },
    { "id": 2, "name": "Django", "slug": "django", "description": "..." }
  ],
  "topics": [
    {
      "id": 1,
      "name": "安装部署",
      "subject_id": 1,
      "subject_name": "Django实战系列",
      "subject_status": "ongoing"
    }
  ]
}
```

### POST /skill/images/upload/

Upload a cover image (PNG/JPG). SVG must be converted to PNG on the client side first.

**Auth:** `Authorization: Token <token>`
**Content-Type:** `multipart/form-data`
**Body field:** `file` (PNG or JPG image)

**Response 201:**
```json
{"success": true, "url": "article/upload/2026/07/17/abc123.png"}
```

Use the returned `url` as the `img_link` value when publishing.

### GET /skill/articles/?slug=\<slug\>

Query an article by slug. Used to determine whether publishing will create or update.

**Auth:** `Authorization: Token <token>`

**Response 200 (exists):**
```json
{"success": true, "exists": true, "article": { "id": 1, "title": "...", ... }}
```

**Response 200 (not found):**
```json
{"success": true, "exists": false}
```

### POST /skill/articles/publish/

Create or update an article. If the slug already exists, the article is **updated**; otherwise a new article is **created**.

**Auth:** `Authorization: Token <token>`

**Request body:**

```json
{
  "title": "文章标题",
  "slug": "article-slug",
  "body": "markdown 正文",
  "summary": "文章摘要",
  "is_publish": false,
  "is_top": false,
  "category": {
    "name": "分类名",
    "slug": "category-slug",
    "description": "SEO描述"
  },
  "tags": [
    { "name": "标签名", "slug": "tag-slug", "description": "SEO描述" }
  ],
  "keywords": ["关键词1", "关键词2"],
  "topic": { "id": 1, "name": "主题名" },
  "topic_order": 99,
  "topic_short_title": ""
}
```

**Response 201 (created) / 200 (updated):**

```json
{
  "success": true,
  "id": 42,
  "url": "/article/article-slug/",
  "title": "文章标题",
  "action": "create"
}
```

`action` is `"create"` for new articles (HTTP 201) or `"update"` for existing articles (HTTP 200).

**Response 400 (error):**

```json
{"success": false, "error": "中文错误描述"}
```

## Field Constraints

All constraints derive from the Django model definitions.

### Article Fields

| Field | Type | Required | Max Length | Default | Notes |
|-------|------|----------|------------|---------|-------|
| `title` | string | **yes** | 150 | — | |
| `slug` | string | **yes** | 50 | — | Unique. Lowercase, hyphens. |
| `body` | string | **yes** | — | — | Raw markdown. |
| `summary` | string | **yes** | 230 | — | AI-generated, not truncated. |
| `is_publish` | boolean | no | — | `false` | Draft mode. When later set to `true`, `create_date` resets to publish time. |
| `is_top` | boolean | no | — | `false` | |
| `img_link` | string | no | — | — | Path from upload API, omit for default image. |

### Category Object

| Field | Type | Required | Max Length | Notes |
|-------|------|----------|------------|-------|
| `name` | string | **yes** | 20 | Not unique (slug is). Lookup uses `.filter().first()`. |
| `slug` | string | **yes** | 50 | Unique. |
| `description` | string | yes | 240 | Default placeholder: "分类描述". |

### Tag Object

| Field | Type | Required | Max Length | Notes |
|-------|------|----------|------------|-------|
| `name` | string | **yes** | 20 | Not unique (slug is). |
| `slug` | string | **yes** | 50 | Unique. |
| `description` | string | yes | 240 | Default placeholder: "标签描述". |

### Topic Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | integer | no | Existing topic: provide id to use directly |
| `name` | string | no | Existing topic: lookup by name. **New topic**: provide name + subject_id to create |
| `subject_id` | integer | no | Required only when creating a new topic. **Subject itself is never created.** |

### Keyword

Array of strings, each ≤20 chars. Get-or-create by name.

## Server-Side Behavior

### Category/Tag: Get-or-Create + Description Update

- If `name` matches existing → reuse, update `description` if the incoming value is better (not the placeholder "分类描述"/"标签描述")
- If `name` is new → create with AI-provided `slug` and `description`
- If `slug` conflicts with an existing different-named record → error

### Topic: Lookup or Create

- Lookup by `id` first, then by `name`
- If found → use existing topic
- If not found AND `subject_id` is provided → create new topic under that subject
- If not found AND no `subject_id` → error with list of available topics
- **Subject is never created** — only existing subjects can be used via `subject_id`

### Keywords: Simple Get-or-Create

- `Keyword.objects.get_or_create(name=name)` for each entry

### Author

Automatically set from the authenticated user (via Token).
