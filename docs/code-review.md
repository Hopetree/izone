# Code Review 报告

**审查范围**：`f87b772` → `7aa89f2`（最近 7 次提交）
**日期**：2026-09-05
**变更文件数**：10 个（便签暗色适配 + 卡片放大查看器 + 导航清理 + 关键词修复 + 日志轮转 + 文档约束）

---

## 问题总览

| # | 优先级 | 文件 | 位置 | 问题概述 | 状态 |
|---|--------|------|------|----------|------|
| 4 | 🟡 建议改进 | `apps/blog/templates/blog/noteIndex.html` | L216-240 | closeViewer 重入保护缺失：关闭动画期间连按 Esc 会重复调度 restore，且 440ms 内无法打开新卡片 | ✅ 已修复 |
| 5 | 🟡 建议改进 | `apps/blog/templates/blog/noteIndex.html` | L247-249 | Esc 关闭查看器与 staff 编辑弹窗冲突：弹窗打开时按 Esc 会关掉底下的查看器 | ✅ 已修复 |
| 6 | 🟡 建议改进 | `apps/blog/templates/blog/noteIndex.html` | L186-193 | 查看器打开期间窗口 resize 会导致大卡片错位（位置尺寸是打开时的固定值） | ✅ 已修复 |
| 7 | 🟡 建议改进 | `supervisord.conf` | L18-22, L33-37 | stdout/stderr 指向同一文件且各自独立轮转，rotate 后 stderr 句柄仍写旧 inode，日志内容会分裂 | ✅ 已修复 |
| 8 | 🟢 可选优化 | `apps/blog/static/blog/css/note.css` | L350 | 死规则：`.note-viewer-card .note-edit-btn + *` 永远匹配不到（编辑按钮是 h2 的最后一个子元素） | ✅ 已修复 |
| 9 | 🟢 可选优化 | `apps/api/serializers.py` | L332-336 | filter→create 之间并发仍可能产生重复 Keyword（与原 get_or_create 竞态相同，非回归），根治需 name 唯一约束 | ⏭️ 保持现状 |

---

## 备注

- #4-#8 已随本次 review 直接修复（本地提交，未推送）。
- #9 保持现状：个人博客并发极低，如需根治再单独排期（name 唯一约束 + 迁移 + 历史数据核查）。
