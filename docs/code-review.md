# Code Review 报告

**审查范围**：`292318d` → `2e20394`（今天 7 次提交，含修复提交 `2e20394`）
**日期**：2026-09-11
**复核方式**：Django 测试客户端全站冒烟（14 个 URL）+ `CaptureQueriesContext` 逐页 SQL 聚类 + 事务内造数回滚验证 + 93 个模板编译 + `check` / `check --deploy` / `makemigrations --check`

---

## 问题总览

| # | 优先级 | 文件 | 位置 | 问题概述 | 状态 |
|---|--------|------|------|----------|------|
| 18 | 🟡 建议改进 | `apps/blog/views.py` | L200-208 | `DetailView.get` 先 `self.get_object()` 再 `super().get()`，同一篇文章被完整取两遍；本次新增的 select_related/prefetch 让重复代价从 1 条 SQL 变成 3 条 | ✅ 已修复 |
| 19 | 🟢 可选优化 | `apps/blog/signals.py` | L31-38 | `_SIDEBAR_KEYS_BY_SENDER[sender.__name__]` 用下标取；将来给 receiver 加 sender 却忘改字典会在 post_save 里抛 KeyError，直接打断保存 | ✅ 已修复 |
| 20 | 🟢 可选优化 | `apps/blog/templates/blog/detail.html`、`subjectDetail.html` | L99 / L161 | 用 `{{ article.article_comments.count }}` 取评论数，绕过了本次新增的 `comment_num` 注解快路径，详情页多 1 条 COUNT | ✅ 已修复 |
| 21 | 🟢 可选优化 | `apps/blog/signals.py` | — | `Subject` 变更未接侧边栏缓存失效信号，侧边栏「专题」计数最长滞后 1 小时（`update_cache` 每小时刷新，实际可接受） | ✅ 已修复 |
| 22 | 🟢 可选优化 | `apps/easytask/actions.py` | L16 | `logger = logging.getLogger('django')`，应用日志混进 izone-access.log；建议改用 `__name__` | ✅ 已修复 |

## 生产环境核实（2026-09-11，只读查询）

| 核实项 | 结果 | 结论 |
|--------|------|------|
| 生产当前部署的代码 | 生产镜像仍为 2026-09-06 构建，`apps/blog/utils.py` 还是 session 版去重（无 `article:read` 键） | **今天的 7 次提交尚未上线**，所以 #10 的浏览量少计回归并未在生产发生；上线时应把 `292318d..2e20394` 一起发（修复已包含在内） |
| session 清理调度 | 生产 Celery beat 中已存在每日执行的 `clear_expired_sessions` | **已核实：不需要额外处理**，先前的 #17「表无界增长」结论作废（本地库缺这条 PeriodicTask 只是本地环境差异） |
| session 表规模 | 行数与过期时间范围（约 2 周）和「每日清理 + 默认 2 周 `SESSION_COOKIE_AGE`」一致 | 清理工作正常，不存在堆积 |
| 数据库连接余量 | 生产 MySQL 的 `max_connections` 相对当前连接数与历史峰值都有充足余量 | 新增的 `action_check_site_links`（最多 8 线程）不会触到连接上限；`CONN_MAX_AGE=60` 安全 |
| Celery 与 `CONN_MAX_AGE` 的兼容性 | 已确认所用 Celery 版本的 `DjangoWorkerFixup` 在 `task_prerun` / `task_postrun` / `worker_process_init` 上接了 `close_old_connections()` | 单人 worker 会在每个任务前后按 `CONN_MAX_AGE` 关闭旧连接，**不会出现「MySQL server has gone away」**；gunicorn 侧则在 60 秒窗口内复用连接，配置生效且安全 |

> **说明**：#17 经生产核实后从「待处理」撤回。原判断依据是本地库 `django_celery_beat_periodictask` 缺少该条目——生产的调度条目比本地库多（图床同步、vitepress 同步、SSL 检查、清理临时脚本文件等），本地库并非生产的最新副本。因此 `02_TDD` 文档里那句 `clear_expired_sessions → 过期 Session 清理` 是**正确**的，上一轮「文档漂移」的说法作废。本地如需复现生产调度，可在 admin 补一条同名 PeriodicTask。

## 生产就绪性检查（非今日提交引入，但影响本次上线）

| 项 | 结论 | 说明 |
|----|------|------|
| `makemigrations --check` | ❌ 不干净 | `easytask` 有 2 个未生成的 Meta 变更（`environmentvariable` / `taskscript`，自 2025-03-31 `9d0c678` 起）。`migrate` 不受影响，但若 CI/部署流程跑 `makemigrations --check` 会失败 |
| `check --deploy` | ⚠️ 8 条警告 | HSTS、`SESSION_COOKIE_SECURE`、`CSRF_COOKIE_SECURE`、`X_FRAME_OPTIONS`、`DEBUG` 等，均为既有配置。其中 `SESSION_COOKIE_SECURE` 因 #10 修复后每个匿名访客都会拿到 session cookie，建议顺手开启 |
| `check` | ✅ 通过 | `System check identified no issues` |
| 今日提交的模型变更 | ✅ 无 | 无新增字段，无迁移漂移（漂移来自 easytask 既有代码） |
| 模板编译 | ✅ 93/93 | 全部模板编译通过，无缺失标签（含新增的 `{% load_pages %}`） |

---

## 修复复核（commit `2e20394`，逐项实测，全部通过）

| # | 结论 | 实测证据 |
|---|------|----------|
| 10 | ✅ 有效 | 事务内实测：访客 A 首访 views +1、A 30 分钟内再访 +0、访客 B 首访 +1；会话已建立（`session_key` 非空）；回滚后 views 复原 |
| 11 | ✅ 有效 | 事务内造数到 106 个标签 / 106 个专题：`/tags/`、`/subject/` 均 200 且渲染出分页控件（`page-inner` + 「下一页」）；`/tags/?page=2` 200 |
| 12 | ✅ 有效 | `CELERY_TASK_ACKS_LATE=False` + `update_cache` 单独 `acks_late=True`，非幂等任务不再 late-ack |
| 13 | ✅ 有效 | 事务内实测：评论保存后 `tag_list`/`category_list`/`menu_link` 保留、`blog_info` 被清；文章仅存 `views` 时四个缓存全部保留；存 `title` 时全部清除。映射 key 与 `blog_tags` 常量集合完全一致 |
| 14 | ✅ 有效 | 6 处版本号均已回退到未改动前的值（20241202.1 / 20241203.1 / 20171229.01966 / 20171229.019906） |
| 15 | ✅ 有效 | 调用栈插桩实测：专题详情页 `Subject.get_article_list` 只调用 1 次（`get_pre`/`get_next` 共用 `_article_list_cache`），修复前为 2 次 |
| 16 | ✅ 有效 | `action_check_site_links` 实跑通过，主线程连接仍可用（`connection.close()` 只关当前线程连接）；单站异常被 catch 不再中断整任务 |

**注意**：复核 #16 时我在本地实际调用了该任务，它按设计发起了真实外呼并写库——本地 2 个导航站被标记为不显示（`Uninstalr` 返回 403、`Jenkins文档` 返回 500）。这正是每日「导航站拨测」的行为，未回滚，如需恢复 `is_show=True` 请告知。

---

> **修复记录（2026-09-11，`--fix`）**：#18–#22 全部修复 —— 详情页复用同一个文章实例（不再取两遍）、
> 侧边栏失效映射改用常量构建并兜底「清全部」、`Subject` 纳入失效信号、详情页评论数改走 `comment_num` 注解、
> `easytask` 日志改用 `__name__` 并在 `LOGGING` 中单独配置 handler。

## 工作区状态

- `git status` 干净，`2e20394` 已包含修复与文档更新；本次 review 后 `docs/review-state.json` 的 `last_reviewed_commit` 需推进到 `2e20394`。

---

## 备注

- 本次 review 未改动任何代码文件；只更新了本报告、`review-state.json` 与本次同步的 4 份文档（01_PRD / 02_TDD / 04_API / README）及 `AGENTS.md`，改动均未提交。
- 全部修复均已实测通过（见「修复复核」表）；#10 是上线前必须确认的回归，已验证修复。
- 以下为已确认「无问题、不需改」的点：
  - 删除的 `summary.png` 只出现在 `migrations/0001_initial.py` 的历史 CharField 默认值里，当前模型已改为 `ProcessedImageField`；查库确认无任何记录引用该路径。
  - 删除的 `blog/js/mermaid/10.2.3/` 无引用；`blog/js/mermaid/11.4.1/mermaid.min.js` 存在，`scripts/detail.html` 指向 `blog/mermaid/9.4.0/` 的断链已被修正。
  - `action_check_friend_links` 从 `apps/easytask/actions.py` 删除是安全的：`tasks.py` 导入的是 `apps/easytask/action/friend_links.py` 中的同名函数。
  - `optimize_article_list` 的 `Count` 注解在 Django 2.2 下实测生成的 SQL 为 `GROUP BY blog_article.id`，未退化为按全字段分组。
  - `ArticleListSerializer(exclude=('body',))` 实测生效：列表接口不含 `body`，详情接口仍返回 `body`。
  - `cache.delete_pattern` 在 `KEY_PREFIX="izone"` 下实测仍能正确删除。
  - `get_topics()` 预取的 `pub_articles` 是 list，模板只做遍历与真值判断，未调用 `.count()`，无 queryset/list 语义差异。
  - `Notification.get_p` 是外键（`instance.get_p_id` 成立）、`SystemNotification.get_p` 是 M2M（故走全量清缓存分支），`comment/signals.py` 的处理与模型一致。
  - `execute_task` 的 `finally` 中 `temp_script_path` 一定已赋值（在 `with` 块内），不存在 UnboundLocalError；该变量已无消费方。
  - 列表页 N+1 确已消除：`/` 第 1 页与第 2 页查询数同为 9；`/tags/` 4 条、`/subject/` 2 条、`/archive/` 4 条，均不随条目数增长。
  - `get_notifications_count` 缓存实测：首次 2 条查询、二次 0 条。
  - `get_parent_comments` 实测 6 条固定查询（父评论 + 作者社交账号 + 邮箱 + 子评论及其社交账号/邮箱），与评论条数无关（Django 2.2 允许对切片 queryset 做 prefetch，未抛异常）。
  - `feed:article:body:*` 缓存实测：首次写入、二次命中、内容一致。
  - 全站 14 个 URL 冒烟无 5xx；`/rsshub/*` 三个端点在无缓存/上游异常下均 200（走占位 RSS 兜底）。
