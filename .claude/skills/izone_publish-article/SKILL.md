---
name: izone_publish-article
description: >
  Write, organize, and publish articles to the izone blog. Supports two modes:
  (1) Writing assistance — draft an article from a topic, outline, or raw notes, or
  organize existing content into well-structured article format.
  (2) Publishing — push a completed article to the blog via API.
  Triggers on: 写文章, 整理文章, 帮我写一篇, 整理成文章, 发布文章, 推送文章,
  publish article, post to blog. Publishing only happens when the user explicitly
  asks to publish or push; writing and organizing can be done independently.
---

# Article Writing and Publishing

This skill has two independent modes:

- **Write/Organize** — Help draft or polish article content. Does NOT publish.
- **Publish** — Push a completed article to the blog. Only on explicit user request.

## Writing Guidelines

Apply these rules to all article content produced by this skill, whether writing from scratch
or organizing existing material.

### Structure

- **Heading hierarchy**: The article body must NOT contain `#` (h1) — the blog page already has a title. Use only `##` (section) and `###` (sub-section). Max 2 levels of body headings. No `####`.
- **Heading numbering**: Prefix `##` with numbers (`## 1.`, `## 2.`). Prefix `###` with sub-numbers (`### 1.1`, `### 1.2`, `### 2.1`).
- **Heading length**: Keep headings short and descriptive. Chinese headings ideally ≤15 chars.
- **Paragraph length**: Break long paragraphs. Aim for 3-5 sentences max per paragraph.
- **Article opening**: Start with a paragraph of context or summary (1-3 sentences), then the first `##` heading. Never start the body directly with a heading — give readers a moment to understand what the article is about.

### Code Blocks

- **Always specify language**: Every fenced code block must have a language identifier.
  Use the correct language (`python`, `bash`, `yaml`, `sql`, `json`, `nginx`, etc.).
  If unsure or no specific language fits, use `text`.
  Never leave the language field empty — `` ``` `` without a language is not allowed.

### Mermaid Diagrams

- Use ` ```mermaid` code blocks for flowcharts, sequence diagrams, timelines, and architecture diagrams.
- Blog renders Mermaid client-side — no server-side rendering needed.
- Use when a diagram makes the concept clearer than text alone. Don't force it — only add when the content benefits from visual explanation.
- Keep diagrams simple: 5-10 nodes max, avoid deeply nested subgraphs.

### Spacing

- **Blank line before headings**: Always one blank line before `##` and `###`.
- **Blank line after headings**: Always one blank line after every heading.
- **Blank line around code blocks**: One blank line before and after fenced code blocks.
- **Blank line around lists**: One blank line before and after ordered/unordered lists.
- **Between paragraphs**: Always separate paragraphs with a blank line.

### Emoji

Do not add decorative emoji to article body. Emoji may only be used when:
- The original content already contains them
- They carry semantic meaning (e.g., warnings, checkmarks in task lists)
- The user explicitly requests them

### Tone

- Write in natural Chinese. Avoid AI-typical patterns: no overly formal transitions like
  "总而言之" "值得注意的是" "综上所述" "不可否认" "众所周知".
- Use concrete examples over abstract explanations. Show code/output rather than describing it.
- Vary sentence length. Mix short direct sentences with longer explanatory ones.
- Read like a knowledgeable colleague writing notes, not a textbook.

### Cover Image (MANDATORY)

**Every article MUST have a custom cover image generated.** This is not optional — always design and upload a cover for each article. The only acceptable reason to skip cover generation is when the upload API returns an error after at least one retry attempt.

To generate and upload a cover image for the article, see [references/cover-design.md](references/cover-design.md) for the full SVG design spec with three layout schemes and color palettes. Quick summary:

- **Size**: 500×300 SVG, server auto-converts to PNG
- **Scheme C (Grid Network)**: **Default/preferred** — grid mesh + glowing nodes + connection lines + title + subtitle + hashtag tags. Best for most technical articles.
- **Scheme A (Icon Row)**: Alternative — glow + label + icons + title + description. Best when you want icon visuals.
- **Scheme B (Minimal Title)**: Minimal — glow + label + larger title + description. Best for essays/notes.
- **MANDATORY font stack**: `'Noto Sans CJK SC','PingFang SC','Microsoft YaHei',sans-serif'`
- **MANDATORY no emoji**: cairosvg cannot render emoji/unicode, use SVG paths for icons

**Upload flow (3 steps, always execute all of them):**

**Step 1 — Generate SVG**: Design the cover following the spec above, write to `/tmp/<slug>-cover.svg`. Pick a palette and background style that matches the article's tone. Never reuse the same palette twice in a row.

**Step 2 — Upload**: Server converts SVG to PNG automatically (no local tools needed).

```bash
curl -s -X POST -H "Authorization: Token $IZONE_API_TOKEN" \
  -F "file=@/tmp/<slug>-cover.svg" \
  "$IZONE_API_BASE/skill/images/upload/"
```

Response: `{"success": true, "url": "article/upload/2026/07/17/abc123.png"}`

**Step 3 — Include in publish**: Add `"img_link": "<url from step 2>"` to the publish JSON payload. Or use `POST /skill/articles/cover/` to update the cover of an already-published article:

```bash
curl -s -X POST -H "Authorization: Token $IZONE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"slug": "<slug>", "img_link": "<url>"}' \
  "$IZONE_API_BASE/skill/articles/cover/"
```

**Error handling**: If the upload fails, retry once with a different file name. If it still fails, proceed without a cover and inform the user that the cover upload failed. Never skip cover generation without attempting it first — only omit `img_link` from the payload when the upload API returns an error after retry.

## Mode 1: Write / Organize

Triggered when user says "写文章", "整理文章", "帮我写一篇", "整理成文章", "draft an article".

### Writing from scratch

When the user provides a topic or outline:

1. Plan the article structure (numbered headings, key points, code examples)
2. Generate a slug from the title
3. **Write the article to `/tmp/<slug>.md`** following Writing Guidelines (mandatory — never present content inline only)
4. Read the file back and present to user
5. Ask: "需要调整什么吗？确认后可以推送到博客。"

Do NOT publish unless the user explicitly asks.

### Organizing existing content

When the user provides raw notes, bullet points, or a rough draft:

1. Preserve all factual content, code, and data
2. Restructure headings to ≤3 levels with numbering
3. Fix spacing (blank lines around headings, code blocks, lists)
4. Ensure all code blocks have language identifiers
5. Remove unnecessary emoji
6. Rewrite AI-flavored phrasing to natural Chinese
7. Write the cleaned article to `/tmp/<slug>.md`
8. Present the cleaned article and ask: "整理完成。需要进一步调整吗？确认后可以推送到博客。"

## Mode 2: Publish

Triggered ONLY when user explicitly says "发布", "推送", "publish", "push to blog", "发布文章".

If the article has not been shown to the user yet (e.g. user provides a file path to publish directly),
follow the full publish flow below. If the article was just written/organized in Mode 1 and is already
visible to the user, skip to Step 4 (metadata matching).

### Step 1: Verify Configuration

Ensure `$IZONE_API_TOKEN` and `$IZONE_API_BASE` are set. See [references/config.md](references/config.md).

### Step 2: Prepare Article File

**MANDATORY: The article body MUST be written to a file before publishing. Never inline the body in a bash command — shell escaping will corrupt code blocks, special characters, and backticks.**

- **From a file path** → Read with Read tool, write to `/tmp/<slug>.md`
- **From conversation content** → Write to `/tmp/<slug>.md` using Write tool
- **Modifying an existing article** → First query to check existence, then write updated content to `/tmp/<slug>.md`

To check if an article already exists by slug:

```bash
curl -s -H "Authorization: Token $IZONE_API_TOKEN" "$IZONE_API_BASE/skill/articles/?slug=<slug>"
```

If `exists: true`, the article already exists. Publishing with the same slug will **update** it.
If `exists: false`, publishing with this slug will **create** a new article.

The `/tmp/<slug>.md` file is the single source of truth for the article body. All subsequent steps read from it.

### Step 3: Parse Metadata

Extract:

| Field | How | Constraint |
|-------|-----|------------|
| `title` | Article topic or first `#` heading from source (if any). Body must not contain `#` headings. | ≤150 chars |
| `slug` | Translate title to English (or pinyin for pure Chinese), lowercase, hyphens | ≤50 chars |
| `summary` | Summarize core content in 2-3 sentences. Chinese ~150-230 chars, English ~100-150 words (roughly equivalent). Don't be too brief — cover the article's main point and scope. | ≤230 chars |
| `body` | The full markdown, with spacing verified | Unmodified |
| `is_publish` | Default `false`（草稿）。If user explicitly says "发布"/"直接发布"/"publish", set `true` | Draft or Published |
| `is_top` | `true` only if user says "置顶" | |
| `img_link` | Cover image path from upload API. **Either provide a valid path, or omit the field entirely. Never set to empty string `\"\"` — causes server error.** | Relative path like `article/upload/2026/07/17/xxx.png` |

### Step 4: Query Metadata

```bash
curl -s -H "Authorization: Token $IZONE_API_TOKEN" "$IZONE_API_BASE/skill/meta/"
```

### Step 5: Match and Assemble

**Category (分类)** — Required. Infer → match against meta → ask user if no match.

**Tags (标签)** — Required (≥1). Match against meta. Reuse existing or create new. Ask user if none clear.

**Topic (主题)** — Required. Match against existing topics. If no match, create new under an existing Subject (专题) via `{"name": "...", "subject_id": <id>}`. **Subject (专题) can never be created** — only use existing ones from the meta query.

See [references/api-spec.md](references/api-spec.md) for full payload structure and field constraints.

### Step 6: Confirm

Present summary and wait for explicit confirmation:

```
确认发布以下文章？

📝 标题: 《<title>》 (<n>字符)
🔗 Slug: <slug>（<新建/更新>）
📂 分类: <name>（已有/新建）
🏷️ 标签: <name>（已有）, <name>（新建）
📖 主题: [<subject>] <topic>
📌 置顶: 否
📄 摘要: <summary>... (<n>字符)
📝 状态: <草稿/直接发布>

确认提交？
```

### Step 7: Publish

Read the body from `/tmp/<slug>.md` (created in Step 2) and publish via Python. This isolates the
article content from the shell, preventing any escaping issues:

```bash
python3 -c "
import json, subprocess, os

with open('/tmp/<slug>.md', 'r') as f:
    body = f.read()

payload = json.dumps({
    'title': '<title>',
    'slug': '<slug>',
    'body': body,
    'summary': '<summary>',
    'is_publish': False,
    'is_top': False,
    'category': {'name': '<name>', 'slug': '<cat-slug>', 'description': '<desc>'},
    'tags': [{'name': '<name>', 'slug': '<tag-slug>', 'description': '<desc>'}],
    'keywords': ['<kw1>', '<kw2>'],
    'topic': {'id': <id>, 'name': '<name>'},  // 已有主题
    // 或新建主题: 'topic': {'name': '<新名称>', 'subject_id': <subject_id>},
}, ensure_ascii=False)

result = subprocess.run([
    'curl', '-s', '-X', 'POST',
    '-H', f'Authorization: Token {os.environ[\"IZONE_API_TOKEN\"]}',
    '-H', 'Content-Type: application/json',
    '-d', payload,
    f'{os.environ[\"IZONE_API_BASE\"]}/skill/articles/publish/',
], capture_output=True, text=True)
print(result.stdout)
"
```

**Always include `img_link`** — add `'img_link': '<uploaded_path>'` to the payload dict. Cover generation is mandatory (see Cover Image section above). Only omit `img_link` if the upload API returned an error after retry — in that case, **omit the key entirely** from the payload dict (do not pass `null`, `\"\"`, or any falsy value).

### Step 8: Confirm Result

**Success (201):**

```
✅ 已保存为草稿！
<full_url>
管理员可直接访问，其他用户需发布后可见。
```

**Error:** Handle per [references/api-spec.md](references/api-spec.md). Slug conflicts: retry up to 3 times.

## Publish Guard

- Never publish without an explicit user request containing "发布" / "推送" / "publish" / "push".
- After Mode 1 (write/organize), offer to publish but do not act until user says yes.
- After publishing, always report the result and the full URL.
