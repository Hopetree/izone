# Code Review 报告

**审查范围**：`cde1b2b3` → `2ca6b0b`
**日期**：2026-07-24
**变更文件数**：15 个（新增 apps/scripts/ 应用 + skill 文档更新 + 配置变更）

---

## 问题总览

| # | 优先级 | 文件 | 位置 | 问题概述 | 状态 |
|---|--------|------|------|----------|------|
| 1 | 🔴 必须修复 | `apps/scripts/models.py` | L48 | `full_command` 属性硬编码了域名 | ✅ 已修复 |
| 2 | 🟡 建议改进 | `apps/scripts/urls.py` | L10 | `/run/` 路径名暗示执行，实际是下载 | ✅ 已修复 |
| 3 | 🟡 建议改进 | `apps/scripts/views.py` | L98-102 | 缓存命中时仍执行 markdown/mermaid 预处理 | ✅ 已修复 |
| 4 | 🟡 建议改进 | `apps/scripts/views.py` | L102 | 脚本缓存 TTL(24h) 与文章缓存(7d)不一致 | ✅ 已修复 |
| 5 | 🟢 可选优化 | `apps/scripts/views.py` | L17-36 | `make_markdown()` 与 blog.views 重复 | ⏭️ 跳过 |

---

## 问题详情

（已修复和跳过的问题详情已移除，只保留待处理问题的详情）
