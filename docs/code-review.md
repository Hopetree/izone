# Code Review 报告

**审查范围**：`292318d` → `36817bc`（今天 6 次提交；`fa87ad0` 一并复核）
**日期**：2026-09-11
**变更文件数**：33 个（详情页/列表页消灭 N+1、缓存与 Session 优化、Celery 配置、RSS 兜底、静态资源懒加载与版本号、mermaid 断链修复）
**diff 规模**：+656 / -1976（含删除未使用的 mermaid 10.2.3 与 summary.png）

---

## 问题总览

| # | 优先级 | 文件 | 位置 | 问题概述 | 状态 |
|---|--------|------|------|----------|------|
| 10 | 🔴 必须修复 | `apps/blog/views.py`、`apps/blog/utils.py` | L175 / L210 | 浏览量 30 分钟去重键缺少访客维度，退化为「全站每 URL 每 30 分钟只计 1 次」，浏览量会大幅少计 | ✅ 已修复 |
| 11 | 🟡 建议改进 | `apps/blog/views.py`、`apps/blog/templates/blog/tagIndex.html` | L513 / L39-43 | `TagListView` 分页 500→100，但模板没有分页控件，标签超过 100 个后会被静默截断、无法翻页 | ✅ 已修复 |
| 12 | 🟡 建议改进 | `izone/settings.py` | L304-309 | 全局开启 `CELERY_TASK_ACKS_LATE`，非幂等任务（脚本执行、推送）在 worker 崩溃后可能被重复执行 | ✅ 已修复 |
| 13 | 🟡 建议改进 | `apps/blog/signals.py` | L29-38 | 侧边栏缓存失效粒度过粗：任何评论增删都会清掉与评论无关的标签/分类/菜单缓存 | ✅ 已修复 |
| 14 | 🟢 可选优化 | 多个模板 | 见详情 | 未改动的静态文件也被提升版本号（monokai-3.css / account.css），导致客户端无谓重新下载 | ✅ 已修复 |
| 15 | 🟢 可选优化 | `apps/blog/models.py` | L265, L284 | `get_pre` / `get_next` 各自执行一次「整专题文章」全量查询，同一请求内重复 | ✅ 已修复 |
| 16 | 🟢 可选优化 | `apps/easytask/actions.py` | L172-195 | `ThreadPoolExecutor` 线程内使用 ORM，线程退出前未关闭数据库连接（配合 `CONN_MAX_AGE=60` 会短暂占用多个连接） | ✅ 已修复 |

---

> **修复记录**：2026-09-11 按 `--fix` 修复 #10–#16 全部问题（浏览量去重补访客维度、分页控件、acks_late 策略、缓存精确失效、回退未改动静态文件版本号、共享专题查询、线程连接关闭）。

---

## 备注

- 本次 review 为只读审查，未改动任何代码文件。
- #10 曾是会立刻影响线上数据的回归（浏览量少计），已在本次 `--fix` 中修复并实测：同一访客 30 分钟内只计 1 次、不同访客各计 1 次。
- 以下为已确认「无问题、不需改」的点（仅记录，不计入问题）：
  - 删除的 `summary.png` 只出现在 `migrations/0001_initial.py` 的历史 CharField 默认值里，当前模型已改为 `ProcessedImageField`；查库确认 99 篇文章无任何记录引用该路径。
  - 删除的 `blog/js/mermaid/10.2.3/` 无引用；`blog/js/mermaid/11.4.1/mermaid.min.js` 存在，`scripts/detail.html` 指向 `blog/mermaid/9.4.0/` 的断链已被修正。
  - `action_check_friend_links` 从 `apps/easytask/actions.py` 删除是安全的：`tasks.py` 导入的是 `apps/easytask/action/friend_links.py` 中的同名函数（被删的是带 `if __name__ == '__main__'` 的重复副本）。
  - `optimize_article_list` 的 `Count` 注解在 Django 2.2 下实测生成的 SQL 为 `GROUP BY blog_article.id`，未退化为按全字段分组。
  - `ArticleListSerializer(exclude=('body',))` 实测生效：列表接口不含 `body`，详情接口仍返回 `body`。
  - `cache.delete_pattern('comment:notif_count:*')` 在设置 `KEY_PREFIX="izone"` 后实测仍能正确删除（探测的 2 个 key 全部命中）。
  - `get_topics()` 预取的 `pub_articles` 是 list，`subject.html` / `subjectDetail.html` 只做遍历与真值判断，未调用 `.count()`，无 queryset/list 语义差异。
  - `Notification.get_p` 是外键（`instance.get_p_id` 成立）、`SystemNotification.get_p` 是 M2M（故走全量清缓存分支），`comment/signals.py` 的处理与模型一致。
  - `manage.py check` 通过；`execute_task` 的 `finally` 中 `temp_script_path` 一定已赋值（在 `with` 块内），不存在 UnboundLocalError；`temp_script_path` 已无任何消费方。
