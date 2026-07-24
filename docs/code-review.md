# Code Review 报告

**审查范围**：`fbf5608` → `73be2d8`
**日期**：2026-07-24
**变更文件数**：6 个（新增 create-script skill + scripts DRF API + .gitignore 修复）

---

## 问题总览

| # | 优先级 | 文件 | 位置 | 问题概述 | 状态 |
|---|--------|------|------|----------|------|
| 1 | 🔴 必须修复 | `apps/scripts/views.py` | L133, L189 | 更新脚本时 `is_publish` 默认值意外取消发布 | ✅ 已修复 |
| 2 | 🟡 建议改进 | `apps/scripts/views.py` | L120-122 | DRF imports 放在文件底部违反 PEP 8 | ✅ 已修复 |
| 3 | 🟡 建议改进 | `apps/scripts/views.py` | L179, L193 | `first()` + `create()` 存在竞态条件 | ✅ 已修复 |

---

## 问题详情

### 🔴 必须修复

#### 1. 更新脚本时 `is_publish` 默认值意外取消发布

- **文件**：`apps/scripts/views.py`
- **位置**：第 133 行（serializer）、第 189 行（view）
- **问题**：`SkillScriptCreateSerializer` 中 `is_publish = BooleanField(default=False)`，DRF 在字段未传入时会将默认值 `False` 写入 `validated_data`。更新路径中 `data.get('is_publish', existing.is_publish)` 的 fallback `existing.is_publish` 永远不会触发——`is_publish` 始终存在于 `validated_data` 中且值为 `False`。结果是：更新已发布脚本的任何字段（如修改描述）都会将其取消发布。create-script 技能文档明确要求"更新时保留现有 `is_publish` 状态"，实际行为与文档相反。
- **当前代码**：
  ```python
  # serializer (L133)
  is_publish = drf_serializers.BooleanField(default=False)

  # view update path (L182-191)
  if is_update:
      existing.title = data['title']
      # ... other fields ...
      existing.is_publish = data.get('is_publish', existing.is_publish)
      existing.save()
  ```
- **修改为**：
  ```python
  # serializer: 去掉 default，让字段可选
  is_publish = drf_serializers.BooleanField(required=False)

  # view: 通过 request.data 判断是否显式传入
  if is_update:
      existing.title = data['title']
      existing.description = data['description']
      existing.code = data['code']
      existing.script_type = data['script_type']
      existing.filename = data['filename']
      existing.run_cmd = data.get('run_cmd', '')
      if 'is_publish' in request.data:
          existing.is_publish = data['is_publish']
      existing.save()
      script = existing
  else:
      script = Script.objects.create(
          title=data['title'],
          slug=slug,
          description=data['description'],
          code=data['code'],
          script_type=data['script_type'],
          filename=data['filename'],
          run_cmd=data.get('run_cmd', ''),
          is_publish=data.get('is_publish', False),
      )
  ```
- **修改说明**：`required=False` 使 DRF 在字段未传入时跳过该字段（不加入 `validated_data`）。更新时通过 `'is_publish' in request.data` 判断是否显式传入，只有在 AI skill 明确传入时才修改发布状态。创建时 `data.get('is_publish', False)` 正确默认草稿。

---

### 🟡 建议改进

#### 2. DRF imports 放在文件底部违反 PEP 8

- **文件**：`apps/scripts/views.py`
- **位置**：第 120-122 行
- **问题**：DRF 相关 import 放在文件底部（在 `script_raw` 函数定义之后），违反 PEP 8 规则（imports 应在文件顶部）。由于 `scripts` app 是无条件加载的（不像 `api` app 有 `API_FLAG` 守卫），如果 DRF 未安装会导致 `ImportError` 使整个 scripts app 加载失败。虽然 DRF 是项目依赖，但这种放置方式既不规范也无实际保护作用。
- **当前代码**：
  ```python
  # ... (line 117, end of script_raw function)
  return response


  from rest_framework.views import APIView
  from rest_framework.response import Response
  from rest_framework import permissions, serializers as drf_serializers
  ```
- **修改为**：
  ```python
  # 移到文件顶部，与其他 third-party imports 放在一起（line 2 附近）
  import markdown
  from rest_framework.views import APIView      # ← 移到这里
  from rest_framework.response import Response   # ←
  from rest_framework import permissions, serializers as drf_serializers  # ←
  from django.conf import settings
  ```
- **修改说明**：与现有 `import markdown` 等第三方 import 放在一起，删除底部重复的 import 块。

#### 3. `first()` + `create()` 存在竞态条件

- **文件**：`apps/scripts/views.py`
- **位置**：第 179 行和第 193 行
- **问题**：`.first()` 检查后 `.create()` 是一个经典的 TOCTOU（time-of-check time-of-use）竞态条件。两个并发请求使用相同 slug 可能同时通过 `existing is None` 检查，然后第一个 `.create()` 成功，第二个因 slug 唯一约束抛出 `IntegrityError`，导致 500 错误。
- **当前代码**：
  ```python
  existing = Script.objects.filter(slug=slug).first()
  is_update = existing is not None

  if is_update:
      # ... update existing ...
  else:
      script = Script.objects.create(...)
  ```
- **修改为**：
  ```python
  script, is_update = Script.objects.update_or_create(
      slug=slug,
      defaults={
          'title': data['title'],
          'description': data['description'],
          'code': data['code'],
          'script_type': data['script_type'],
          'filename': data['filename'],
          'run_cmd': data.get('run_cmd', ''),
      }
  )
  # 创建时设置 is_publish 默认值，更新时保留现有值
  if is_update:
      if 'is_publish' in request.data:
          script.is_publish = data['is_publish']
          script.save(update_fields=['is_publish'])
  else:
      script.is_publish = data.get('is_publish', False)
      script.save(update_fields=['is_publish'])
  ```
- **修改说明**：`update_or_create` 是原子操作（在 unique 字段上使用 `get_or_create` 的变体），消除了竞态条件。创建时手动设置 `is_publish` 默认值（因为 `update_or_create` 的 `defaults` 在更新时也会被应用，不适合直接放 `is_publish`）。
