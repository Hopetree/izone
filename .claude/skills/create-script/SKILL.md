---
name: create-script
description: >
  Create and publish executable shell or Python scripts to the izone blog's
  script sharing platform. Helps draft script code and documentation,
  then pushes to the server via API. Triggers on: 创建脚本, 新建脚本,
  写脚本, 分享脚本, 制作脚本, create script, new script.
---

# Script Creation and Publishing

Create executable scripts (Shell or Python) and publish them to the blog's script sharing platform.

## Script Model

| Field | Constraint | Description |
|-------|-----------|-------------|
| `title` | ≤150 chars | Script title |
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

## Workflow

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

### Step 4: Create via API

```bash
curl -s -X POST \
  -H "Authorization: Token $IZONE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<title>",
    "slug": "<slug>",
    "description": "<description>",
    "code": "<code>",
    "script_type": "shell|python",
    "filename": "<filename>",
    "run_cmd": "<run_cmd>",
    "is_publish": false
  }' \
  "$IZONE_API_BASE/skill/scripts/create/"
```

**MANDATORY: Write code to `/tmp/<slug>.sh` or `/tmp/<slug>.py` first, then read from file in Python.** Never inline code in bash — shell escaping will corrupt special characters.

Use Python to publish:

```bash
python3 -c "
import json, subprocess, os

with open('/tmp/<slug>.sh', 'r') as f:
    code = f.read()

payload = json.dumps({
    'title': '<title>',
    'slug': '<slug>',
    'description': '<description>',
    'code': code,
    'script_type': 'shell',
    'filename': '<filename>',
    'run_cmd': '<run_cmd>',
    'is_publish': False,
}, ensure_ascii=False)

result = subprocess.run([
    'curl', '-s', '-X', 'POST',
    '-H', f'Authorization: Token {os.environ[\"IZONE_API_TOKEN\"]}',
    '-H', 'Content-Type: application/json',
    '-d', payload,
    f'{os.environ[\"IZONE_API_BASE\"]}/skill/scripts/create/',
], capture_output=True, text=True)
print(result.stdout)
"
```

### Step 5: Result

**Success (201):**
```
✅ 脚本已创建！
查看: https://tendcode.com/scripts/<slug>/
状态: 草稿（需在详情页点击"发布"后用户才能下载）

提示: 访问 https://tendcode.com/scripts/<slug>/ 可预览和发布。
```

**Error:** If slug exists, suggest an alternative slug and retry.

## Configuration

Requires `$IZONE_API_TOKEN` and `$IZONE_API_BASE` environment variables. See [references/config.md](references/config.md).

## Publish Guard

- Scripts default to `is_publish: false` (draft)
- Only set `is_publish: true` if user explicitly says "直接发布" or "发布"
- Unpublished scripts cannot be downloaded by users
