---
name: izone-publish-article
version: 1.3
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
- **Heading length**: Keep headings short and descriptive. **Chinese headings must NOT exceed 15 characters**（二级/三级标题正文字数 ≤15 个中文长度，不含编号前缀 `1.`/`1.1`；超过会破坏博客标题导航的显示效果。用户约定 2026-09-12，同日由 13 调整为 15）。
- **Paragraph length**: Break long paragraphs. Aim for 3-5 sentences max per paragraph.
- **Article opening**: Start with a paragraph of context or summary (1-3 sentences), then the first `##` heading. Never start the body directly with a heading — give readers a moment to understand what the article is about.

### Code Blocks

- **Always specify language**: Every fenced code block must have a language identifier.
  Use the correct language (`python`, `bash`, `yaml`, `sql`, `json`, `nginx`, etc.).
  If unsure or no specific language fits, use `text`.
  Never leave the language field empty — `` ``` `` without a language is not allowed.

### Markdown Extensions (beyond standard Markdown)

The blog renders articles with a custom extension set, so a small number of non-standard syntaxes
are available. **Read [references/markdown-extensions.md](references/markdown-extensions.md) before
using any of them** — it has the verified syntax, the rendered HTML, and the failure modes.

Quick map of what's available and when it earns its place:

| Need | Syntax | Note |
|------|--------|------|
| Same logic in several languages | `:::: code-group` + `::: code-item <Name>` | Renders as tabs. Label must be one word. |
| Warning / prerequisite / gotcha | `::: warning <word>` / `::: danger <word>` | Bootstrap alert. Title must be one word. |
| Supplementary aside | `::: info <word>` / `::: primary <word>` | Also `secondary`, `success`. |
| Show what changed (old → new) | `~~old~~` | `<del>` |
| Inline emphasis / status | `icon:home` | FontAwesome **4.7** names only. Use sparingly. |
| Flowchart, sequence, architecture | ` ```mermaid` | Rendered client-side by mermaid 11.4.1. |
| Checklist, migration progress | `- [x]` / `- [ ]` | Read-only checkboxes. |
| Source citation, side note | `[^1]` | Footnotes collect at the end of the article. |

**Two rules that break these silently — always follow them:**

1. **Every fence (```` ``` ```` and `:::` / `::::`) must start at column 0.** An indented Mermaid
   fence degrades into a garbled inline-code paragraph; an indented `:::` / `::::` is not recognized
   at all and leaks as literal text.
2. **Put a blank line after a `:::` opening fence.** Alert titles are parsed by splitting the block,
   so text jammed against the fence gets swallowed as the title or kills the whole block.

**Also keep in mind:**

- Titles on `:::` blocks and tab labels on `code-item` must be a **single word** (no spaces).
- Icons are not validated: a wrong name renders an invisible icon rather than an error. Only use the
  names listed in the reference.
- Don't use extensions for their own sake. One or two alerts per article, icons as occasional inline
  emphasis — not as bullet markers. Plain Markdown stays the default.

### Mermaid Diagrams

- Use ` ```mermaid` code blocks for flowcharts, sequence diagrams, timelines, and architecture diagrams.
- Blog renders Mermaid client-side — no server-side rendering needed.
- Use when a diagram makes the concept clearer than text alone. Don't force it — only add when the content benefits from visual explanation.
- Keep diagrams simple: 5-10 nodes max, avoid deeply nested subgraphs.
- The fence must be at column 0 and `` ```mermaid `` must not carry trailing content on the same line.

### Spacing

- **Blank line before headings**: Always one blank line before `##` and `###`.
- **Blank line after headings**: Always one blank line after every heading.
- **Blank line around code blocks**: One blank line before and after fenced code blocks.
- **Blank line around lists**: One blank line before and after ordered/unordered lists.
- **Between paragraphs**: Always separate paragraphs with a blank line.

### Emoji

不要滥用 emoji，也不要在正文里为了"可爱"堆砌装饰性 emoji。有必要的时候可以用，让文章更鲜活：

- 需要表达语气或态度时（如警告 ⚠️、重点 ✅、结果 🎉）
- 列表或任务清单中用作标记
- 原文内容本身就包含 emoji
- 用户明确要求

判断标准：删掉这个 emoji 会让表达变弱，就用；删掉毫无影响，就别用。避免连续多个 emoji 堆砌。

### Tone

- Write in natural Chinese. Avoid AI-typical patterns: no overly formal transitions like
  "总而言之" "值得注意的是" "综上所述" "不可否认" "众所周知".
- Use concrete examples over abstract explanations. Show code/output rather than describing it.
- Vary sentence length. Mix short direct sentences with longer explanatory ones.
- Read like a knowledgeable colleague writing notes, not a textbook.

### Privacy Sanitization (MANDATORY — 隐私纪律，发布前必须执行)

**对外发布的文章严禁出现任何真实内部信息。** 这是用户硬性要求（2026-09-10 首次固化，2026-09-11 因博客暴露真实 IP 强化），适用于写作与发布全流程。

写正文时**默认用泛化占位**，不要写真实值：

- **IP 地址** → 一律用 RFC 5737 保留测试地址：`203.0.113.x` / `198.51.100.x` / `192.0.2.x`
- **真实域名/子域名** → 用 `example.com` 泛化（如 `share.example.com`）；不要写客户/自己服务的真实域名
- **主机标识/编号** → 用「生产主机」「内网主机」等描述，不写 `106`/`203`/`114` 这类主机代号
- **内部渠道/命名/拓扑** → 用 `渠道 A/B/C`、`客户端 A` 等占位，不暴露内部编号、渠道对应关系、实例拓扑
- **凭据/邮箱/内网网段** → 一律不出现（`192.168.x`、`10.x`、`172.16-31.x`）
- **证书编号如 npm-17、时间戳、端口** 属于技术示例，可保留

**发布前必须执行自检**（发布流程的最后一步，不可跳过）：对正文跑一次 grep，确认无残留：

```bash
grep -nE "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" /tmp/<slug>.md
grep -nE "[a-z0-9-]+\.(com|net|cn|org)" /tmp/<slug>.md
grep -nE "192\.168|172\.1[0-9]\.|10\.[0-9]+\." /tmp/<slug>.md
```

以上任一命中真实内部信息（`127.0.0.1`、`example.com`、RFC 5737 保留地址除外），先替换再发布。

### Cover Image (MANDATORY)

**Every article MUST have a custom cover image generated.** This is not optional — always design and upload a cover for each article. The only acceptable reason to skip cover generation is when the upload API returns an error after at least one retry attempt.

To generate and upload a cover image for the article, see [references/cover-design.md](references/cover-design.md) for the full SVG design spec with three layout schemes and color palettes. Quick summary:

- **Size**: 500×300 SVG, server auto-converts to PNG
- **Scheme C (Grid Network)**: **Default/preferred** — grid mesh + glowing nodes + connection lines + title + subtitle + hashtag tags. Best for most technical articles.
- **Scheme A (Icon Row)**: Alternative — glow + label + icons + title + description. Best when you want icon visuals.
- **Scheme B (Minimal Title)**: Minimal — glow + label + larger title + description. Best for essays/notes.
- **MANDATORY font stack**: `'Noto Sans CJK SC','PingFang SC','Microsoft YaHei',sans-serif'`
- **MANDATORY no emoji (cover SVG only)**: cairosvg cannot render emoji/unicode in cover images, use SVG paths for icons. 仅封面技术限制，正文 emoji 使用遵循上方 Emoji 规则。

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

1. Plan the article structure (numbered headings, key points, code examples). If the content
   involves multiple languages for one example, a version warning, a before/after comparison, or a
   diagram, pick the matching extension syntax from [references/markdown-extensions.md](references/markdown-extensions.md)
   and re-check the two fence rules before writing.
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
5. Remove overused/decorative emoji (keep meaningful ones)
6. Rewrite AI-flavored phrasing to natural Chinese
7. **Re-check any `:::` / code-group fences survived the edit** — opening fence at column 0 with a
   blank line after it, single-word titles and tab labels. Restructuring easily reflows the blank
   line that alerts depend on, and a broken alert silently renders as literal `:::` text.
8. Write the cleaned article to `/tmp/<slug>.md`
9. Present the cleaned article and ask: "整理完成。需要进一步调整吗？确认后可以推送到博客。"

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

**Topic short title & order (主题短标题与排序)** — For series articles sharing one topic, also send `topic_short_title` (主题菜单显示的短标题，建议 "篇号 + 短关键词"，如 `01 先立规矩再干活`) and `topic_order` (篇号数字：01→1、02→2…). These keep the topic menu ordered and readable. 详见 [references/api-spec.md](references/api-spec.md) 的 Article Fields。

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

### Step 6.5: Privacy Check (MANDATORY — 隐私自检，不可跳过)

**发布前必须对 `/tmp/<slug>.md` 执行隐私自检。** 这是用户硬性要求（2026-09-11 因真实 IP 暴露事故强化），发现真实内部信息先替换再发布。

```bash
grep -nE "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" /tmp/<slug>.md
grep -nE "[a-z0-9-]+\.(com|net|cn|org)" /tmp/<slug>.md
grep -nE "192\.168|172\.1[0-9]\.|10\.[0-9]+\." /tmp/<slug>.md
grep -nE "(^|[^0-9])(106|203|114|168)([^0-9]|$)" /tmp/<slug>.md   # 主机代号
```

**放行白名单**（命中可保留）：`127.0.0.1`、`example.com`、RFC 5737 保留地址（`203.0.113.x`/`198.51.100.x`/`192.0.2.x`）、`localhost`。

**违规处理**：任何一条命中真实内部信息 → 先替换为泛化占位（见 Writing Guidelines 的 Privacy Sanitization 节）→ 重新检查 → 通过后才进入 Step 7。**绝不带着真实 IP/域名/主机代号发布。**

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
    // 系列文章可选：主题菜单短标题 + 篇号排序
    // 'topic_short_title': '01 先立规矩再干活',
    // 'topic_order': 1,
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

## Self-Review（自省四问 · 每次执行完毕后强制执行）

**本技能无论执行哪个模式（Write/Organize/Publish），任务收尾前都必须自省。** 自省的目标是「越用越好用」——每次执行都让流程更可靠、文档更清楚；发现问题直接自我优化，有不确定项就提出来问用户。自省不是可选步骤。

### 自省四问（逐条对照检查）

**1) 技能描述与实际行为是否一致（参数/路径/输出/退出码/阈值）**

- 文件：正文是否真实写入 `/tmp/<slug>.md`，且该文件是唯一正文来源（严禁把 body 内联进 bash 命令）
- 元数据：`slug` 小写连字符且 ≤50 字符、`title` ≤150 字符、`summary` ≤230 字符，与 Step 3 解析结果逐项一致
- 正文规范：无 `#`/`####`、`##`/`###` 带编号、中文标题 ≤15 字（不含编号）、所有代码块带语言标识、间距合规
- 封面：`img_link` 与上传 API 返回的 url **逐字一致**（不得凭空捏造路径）；上传失败重试 1 次后才允许省略，且省略时该 key 必须从 payload 中完全移除
- 状态：`is_publish`/`is_top` 与用户指令一致；API 退出码/响应符合预期（发布 201、上传/cover `{"success": true}`），非预期响应是否按 api-spec 处理

**2) 本次有没有误报、漏报**

- 隐私自检：真实 IP/域名/主机代号有没有漏网；白名单（`127.0.0.1`、`example.com`、RFC 5737、`localhost`）有没有被误报
- 新建/更新：`exists` 判断与后端实际状态是否一致（该更新的没更新、该新建的覆盖了旧文）
- 分类/标签/主题：声称「新建」的项是否确实不存在（避免重复创建）

**3) 分类、级别、阈值、措辞有没有噪音**

- 分类/标签/专题命名是否贴合 meta 已有风格，有无冗余新建或命名不一致
- `summary` 长度是否落在 150~230 字区间、信息密度是否合适（不空泛、不堆砌）
- 标题 ≤15 字检查、emoji 使用、Step 6 确认措辞是否清晰，有没有不必要的重复询问

**4) 执行本身有没有报错、变慢、护栏被绕过、安全风险**

- 报错/重试：slug 冲突重试 ≤3 次、cover 上传重试 1 次的路径是否处理干净，最终结果如实报告
- 护栏：发布是否获得用户显式确认；Publish Guard 有没有被绕过；隐私自检有没有被跳过
- 安全：token/内部信息是否进入日志、命令输出或正文；`/tmp/<slug>.md`、cover svg 等临时文件是否残留；工作区有没有散落未归档产物

### 自省输出格式

每次执行完毕后，在给用户的最终回复末尾追加自省信息：

- **一切正常**：只写一行，不展开——
  `✅ 自省四问：描述/行为一致，无误报漏报，无噪音，执行/护栏/安全正常（见技能变更记录则附最新记录）`
- **发现问题**：才展开完整四问，逐条标注 ⚠️/❓，并说明问题、修正动作或待确认项：

```
📋 自省四问 · <技能名> v<版本号>
1. 描述 vs 行为：⚠️ <一句话结论>
2. 误报/漏报：⚠️ <一句话结论>
3. 噪音：⚠️ <一句话结论>
4. 报错/护栏/安全：⚠️ <一句话结论>

结论：已自我优化（见下方变更记录）/ ❓ 有不确定项需用户确认
```

### 自我优化规则

- **技能文档自身缺陷**（阈值、步骤、措辞没说清、路径写错、规则矛盾）→ 不请示，立即执行：更新 SKILL.md 或 references/*.md，并在下方「技能变更记录」追加一行，然后在自省块中告知用户改了什么、为什么。
- **本次执行行为偏差**（漏做某步、用错参数、输出与描述不符）→ 修正本次结果，在自省块中如实标注；若偏差暴露了技能文档漏洞，按上一条更新技能。
- **不确定、或可能影响其他技能的决策**（如改阈值、改共享流程）→ 不擅自改，在自省块中标注 ❓ 并直接向用户提问。

## 技能变更记录

- 2026-09-14 v1.1：新增「自省四问」Self-Review 章节 + 技能变更记录。每次执行完毕强制自省（四问：描述一致性/误报漏报/噪音/执行与安全），发现技能缺陷直接自我优化并记录，不确定项向用户提问。
- 2026-09-14 v1.2：自省输出收敛——一切正常时只写一行 `✅ 自省四问：...`，发现问题才展开详细四问；明确自省目的为「越用越好用」（自我更新本身就是沉淀）。
- 2026-09-15 v1.3：合并远程更新（commit 1f53f72）——新增「Markdown Extensions」章节与 references/markdown-extensions.md（已实测验证的渲染扩展语法参考：代码组/提示块/删除线/图标 FA4.7/Mermaid/任务清单/脚注）；Mermaid 铁律（围栏顶格、开围栏行不带尾随内容）；Write/Organize 步骤加扩展语法选择与围栏复查钩子。
