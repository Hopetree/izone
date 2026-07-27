---
name: izone-publish-script
description: >
  Create, update, and publish executable shell or Python scripts to the izone
  blog's script sharing platform. Helps draft script code and documentation,
  then pushes to the server via API. Supports both creating new scripts and
  updating existing ones (including publish status). Triggers on: 创建脚本,
  新建脚本, 写脚本, 分享脚本, 制作脚本, 更新脚本, 修改脚本, create script,
  new script, update script.
---

# Script Creation, Update, and Publishing

Create or update executable scripts (Shell or Python) on the blog's script sharing platform. The API uses slug-based upsert: same slug creates or updates.

## Script Model

| Field | Constraint | Description |
|-------|-----------|-------------|
| `title` | ≤30中文字/50英文字母 | Script title, keep it concise |
| `slug` | ≤50 chars, unique | URL identifier, English/pinyin |
| `description` | Markdown | Documentation (usage, prerequisites, notes) |
| `code` | Raw text | The script code itself |
| `script_type` | `shell` or `python` | Script type |
| `filename` | ≤100 chars | Download filename, e.g. `install-docker.sh` |
| `run_cmd` | ≤500 chars | Post-download execution command, e.g. `sudo bash install-docker.sh` |
| `is_publish` | bool, default `false` | Whether the script is downloadable |

## Writing Guidelines

### Code

- Always include a shebang: `#!/bin/bash` or `#!/usr/bin/env python3`
- Use `set -e` for shell scripts (fail on error)
- Add inline comments explaining key steps
- Keep scripts self-contained, single-file
- Test commands like `apt-get` should include `-y` flag for non-interactive use
- Avoid hardcoding sensitive values (passwords, tokens) — use variables
- **Target mainland Chinese users**: Scripts must pre-configure China-friendly defaults:
  - GitHub downloads: provide `-m` mirror option, default mirror `https://ghproxy.net/`
  - pip sources: default to `https://pypi.tuna.tsinghua.edu.cn/simple`
  - APT sources: suggest Tsinghua/Aliyun mirrors in comments
  - Docker images: suggest registry mirrors for pulling
  - Any foreign-hosted resources should have a mirror parameter or fallback

### Description (Markdown)

- Start with a brief intro of what the script does
- List supported systems (OS, versions, dependencies)
- Explain prerequisites if any
- Provide usage examples
- Follow blog article writing conventions: no h1, use `##` headings, code blocks with language tags

### Run Command

The `run_cmd` is what users execute AFTER downloading. The system auto-generates:
```
curl -o <filename> <download-url>
```
And appends `&& <run_cmd>`. So `run_cmd` should reference the same `filename`:
- Shell: `sudo /bin/bash install-docker.sh` or `bash setup.sh`
- Python: `python3 batch-rename.py`

## Modes

This skill has two modes, determined by whether the script already exists:

- **Create** — New script, generate slug and all fields from scratch.
- **Update** — Existing script, query current state, modify specified fields only.

## Workflow

### Step 0: Check if Script Exists

If the user references an existing script, query first to see current state:

```bash
curl -s -H "Authorization: Token $IZONE_ADMIN_TOKEN" \
  "$IZONE_API_BASE/skill/scripts/?slug=<slug>" | python3 -m json.tool
```

Response for existing script:
```json
{
  "success": true,
  "exists": true,
  "script": {
    "title": "...", "slug": "...", "description": "...",
    "code": "...", "script_type": "shell", "filename": "...",
    "run_cmd": "...", "is_publish": false,
    "create_date": "2026-07-24 12:00", "update_date": "2026-07-24 12:00"
  }
}
```

Response when not found: `{"success": true, "exists": false}`

**When updating:**
- If `exists: true`, confirm with user what fields to change, keep others as-is
- If user only asks to change one field (e.g. "更新描述"), only modify that field, preserve all others
- If `exists: false`, proceed as new creation

### Step 1: Gather Requirements

Ask the user:
- What does the script do?
- Shell or Python?
- Any special execution flags?

If the user provides minimal input ("帮我写一个安装nginx的脚本"), fill in the gaps yourself.

### Step 2: Draft

Generate:
1. **Slug** — English/pinyin from title, lowercase, hyphens
2. **Code** — following Writing Guidelines
3. **Description** — markdown documentation
4. **Filename** — e.g. `install-nginx.sh`
5. **Run command** — e.g. `sudo /bin/bash install-nginx.sh`

### Step 3: Confirm

Present to user:

```
确认创建以下脚本？

📝 标题: <title>
🔗 Slug: <slug>
📄 文件名: <filename>
📟 类型: Shell / Python
💻 代码: <n>行
⚡ 一键命令: curl -o <filename> <url> && <run_cmd>
📝 状态: 草稿（不提供下载）

确认创建？
```

### Step 4: Save via API (Create or Update)

The endpoint `POST /skill/scripts/save/` handles both creation and update. If the slug exists, it updates; otherwise creates.

**⚠️ MANDATORY: Write description and code to temporary files first, then read them in Python to build the payload.** Never inline markdown or code in a bash command — shell escaping will corrupt backticks, special characters, and code blocks, causing data loss. This is the same pattern as the article publish skill.

**Step 4a — Write temp files:**

- Code → `/tmp/<slug>.sh` or `/tmp/<slug>.py` (the script code)
- Description → `/tmp/<slug>-desc.md` (the markdown description)

**Step 4b — Publish via Python:**

```bash
python3 -c "
import json, subprocess, os

with open('/tmp/<slug>.sh', 'r') as f:
    code = f.read()
with open('/tmp/<slug>-desc.md', 'r') as f:
    description = f.read()

payload = json.dumps({
    'title': '<title>',
    'slug': '<slug>',
    'description': description,
    'code': code,
    'script_type': 'shell',
    'filename': '<filename>',
    'run_cmd': '<run_cmd>',
    'is_publish': False,
}, ensure_ascii=False)

result = subprocess.run([
    'curl', '-s', '-X', 'POST',
    '-H', f'Authorization: Token {os.environ[\"IZONE_ADMIN_TOKEN\"]}',
    '-H', 'Content-Type: application/json',
    '-d', payload,
    f'{os.environ[\"IZONE_API_BASE\"]}/skill/scripts/save/',
], capture_output=True, text=True)
print(result.stdout)
"
```

### Step 5: Result

**Create (201):**
```
✅ 脚本已创建！
查看: https://tendcode.com/scripts/<slug>/
状态: 草稿

提示: 访问详情页点击"发布"按钮后用户才能下载。
```

**Update (200):**
```
✅ 脚本已更新！
查看: https://tendcode.com/scripts/<slug>/
```

**Error:** Slug conflict or validation error — read the error message and fix.

## Configuration

Requires `$IZONE_ADMIN_TOKEN` and `$IZONE_API_BASE` environment variables. See [references/config.md](references/config.md).

## Publish Guard

- New scripts default to `is_publish: false` (draft)
- When updating, preserve existing `is_publish` unless user explicitly asks to change it
- Only set `is_publish: true` if user explicitly says "发布" or "直接发布"
- Set `is_publish: false` only if user explicitly says "取消发布" or "下架"
- Unpublished scripts cannot be downloaded by users (404)
