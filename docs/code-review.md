# Code Review 报告

**审查范围**：`292318d` → `9c30f5a`（2026-09-11 的 9 次提交，含三轮修复 `2e20394`、`55c3d86`、`9c30f5a`）
**日期**：2026-09-11
**复核方式**：Django 测试客户端全站冒烟（19 个 URL）+ `CaptureQueriesContext` 逐页 SQL 实测 + 事务内造数回滚验证 + 93 个模板编译 + 真实响应头核对 cookie 标记 + `check` / `check --deploy` / `makemigrations --check` / `sqlmigrate` + 生产环境只读核实

---

## 问题总览（待处理）

| # | 优先级 | 文件 | 位置 | 问题概述 | 状态 |
|---|--------|------|------|----------|------|
| 23 | 🟢 可选优化 | `izone/settings.py` | L281、L370（另见 L119） | 同一个 `IZONE_PROTOCOL_HTTPS` 被独立派生两次、命名还不一致（`IS_HTTPS` / `PROTOCOL_HTTPS`）；若日后只改一处，cookie 的 Secure 标记会与 sitemap/绝对链接的协议判断不一致 | ✅ 已修复 |
| 24 | 🟢 可选优化 | `docs/code-review.md` | L30 | 「`check --deploy` 已消除 2 条」未标注前提：实测**默认环境仍是 8 条**（W012/W016 仍在），只有 `IZONE_PROTOCOL_HTTPS=https` 时才是 6 条；同表其它行与环境无关，复核者容易误判报告写错 | ✅ 已修复 |
| 25 | 🟢 可选优化 | `apps/easytask/migrations/0002_auto_20260911_1413.py` | — | 迁移文件仍是 untracked（`??`），但本地库已把它记为 applied（`showmigrations` 显示 `[X]`）；若不随提交纳入，其它环境或后续 `makemigrations` 会碰到「已应用但无对应文件」 | ✅ 已修复 |

> 本轮仅 3 项 🟢，无 🔴/🟡：安全配置本身经实测有效（见「生产环境核实」与「问题详情 #23」的实测证据）。

## 生产环境核实（2026-09-11，只读查询）

| 核实项 | 结果 | 结论 |
|--------|------|------|
| 生产当前部署的代码 | 生产镜像仍为 2026-09-06 构建，`apps/blog/utils.py` 还是 session 版去重（无 `article:read` 键） | **今天的 8 次提交尚未上线**，所以 #10 的浏览量少计回归并未在生产发生；上线时应把 `292318d..55c3d86` 一起发（修复已包含在内） |
| session 清理调度 | 生产 Celery beat 中已存在每日执行的 `clear_expired_sessions` | **已核实：不需要额外处理**，先前的 #17「表无界增长」结论作废（本地库缺这条 PeriodicTask 只是本地环境差异） |
| session 表规模 | 行数与过期时间范围（约 2 周）和「每日清理 + 默认 2 周 `SESSION_COOKIE_AGE`」一致 | 清理工作正常，不存在堆积 |
| 数据库连接余量 | 生产 MySQL 的 `max_connections` 相对当前连接数与历史峰值都有充足余量 | 新增的 `action_check_site_links`（最多 8 线程）不会触到连接上限；`CONN_MAX_AGE=60` 安全 |
| HTTPS / 安全相关环境变量 | 生产 `izone_web` 容器 env 中确实存在 `IZONE_PROTOCOL_HTTPS=https` 与 `IZONE_DEBUG=False`（compose `.env` 内未直接命中，变量由 compose `environment:` 提供） | 新增的 `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` 上线后**会真实生效**，不是空配置；本地实测同一条 session cookie 的 `secure` 标记随该变量在 空 / `True` 之间正确切换 |
| Celery 与 `CONN_MAX_AGE` 的兼容性 | 已确认所用 Celery 版本的 `DjangoWorkerFixup` 在 `task_prerun` / `task_postrun` / `worker_process_init` 上接了 `close_old_connections()` | 单人 worker 会在每个任务前后按 `CONN_MAX_AGE` 关闭旧连接，**不会出现「MySQL server has gone away」**；gunicorn 侧则在 60 秒窗口内复用连接，配置生效且安全 |

> **说明**：#17 经生产核实后从「待处理」撤回。原判断依据是本地库 `django_celery_beat_periodictask` 缺少该条目——生产的调度条目比本地库多（图床同步、vitepress 同步、SSL 检查、清理临时脚本文件等），本地库并非生产的最新副本。因此 `02_TDD` 文档里那句 `clear_expired_sessions → 过期 Session 清理` 是**正确**的，上一轮「文档漂移」的说法作废。本地如需复现生产调度，可在 admin 补一条同名 PeriodicTask。

## 生产就绪性检查（非今日提交引入，但影响本次上线）

| 项 | 结论 | 说明 |
|----|------|------|
| `makemigrations --check` | ✅ 已干净 | 2026-09-11 补生成 `easytask/migrations/0002_auto_20260911_1413.py`（两处 `AlterModelOptions`：`ordering` + `verbose_name`，纯状态操作、无 DDL），本地已应用；`--check` 现输出 "No changes detected"。此后该检查可作为真实漂移的哨兵 |
| `check --deploy` | ⚠️ 6 条警告（前提：`IZONE_PROTOCOL_HTTPS=https`） | 在该变量**已设置**时消除 `SESSION_COOKIE_SECURE`、`CSRF_COOKIE_SECURE` 两条；**默认环境（该变量未设置）仍为 8 条**（W012/W016 仍在），本地/CI 复核请带上该变量再比对，避免误判本报告失真。剩余：HSTS(W004，另行评估)、`SECURE_CONTENT_TYPE_NOSNIFF`(W006)、`SECURE_BROWSER_XSS_FILTER`(W007，该响应头已被浏览器废弃可忽略)、`SECURE_SSL_REDIRECT`(W008，**故意不开**：未配 `SECURE_PROXY_SSL_HEADER`，开启会与边缘 301 形成重定向循环)、DEBUG(W018，生产 `IZONE_DEBUG=False` 不会触发)、`X_FRAME_OPTIONS`(W019，实际值已是 `SAMEORIGIN`) |
| `check` | ✅ 通过 | `System check identified no issues` |
| 今日提交的模型变更 | ✅ 无 | 无新增字段，无迁移漂移（漂移来自 easytask 既有代码） |
| 模板编译 | ✅ 93/93 | 全部模板编译通过，无缺失标签（含新增的 `{% load_pages %}` 与两处 `{% get_comment_count %}`） |

---

## 修复复核

### 第一轮：commit `2e20394`

| # | 结论 | 实测证据 |
|---|------|----------|
| 10 | ✅ 有效 | 事务内实测：访客 A 首访 views +1、A 30 分钟内再访 +0、访客 B 首访 +1；会话已建立（`session_key` 非空）；回滚后 views 复原 |
| 11 | ✅ 有效 | 事务内造数到 106 个标签 / 106 个专题：`/tags/`、`/subject/` 均 200 且渲染出分页控件（`page-inner` + 「下一页」）；`/tags/?page=2` 200 |
| 12 | ✅ 有效 | `CELERY_TASK_ACKS_LATE=False` + `update_cache` 单独 `acks_late=True`，非幂等任务不再 late-ack |
| 13 | ✅ 有效 | 事务内实测：评论保存后 `tag_list`/`category_list`/`menu_link` 保留、`blog_info` 被清；文章仅存 `views` 时四个缓存全部保留；存 `title` 时全部清除。映射 key 与 `blog_tags` 常量集合完全一致 |
| 14 | ✅ 有效 | 6 处版本号均已回退到未改动前的值（20241202.1 / 20241203.1 / 20171229.01966 / 20171229.019906） |
| 15 | ✅ 有效 | 调用栈插桩实测：专题详情页 `Subject.get_article_list` 只调用 1 次（`get_pre`/`get_next` 共用 `_article_list_cache`），修复前为 2 次 |
| 16 | ✅ 有效 | `action_check_site_links` 实跑通过，主线程连接仍可用（`connection.close()` 只关当前线程连接）；单站异常被 catch 不再中断整任务 |
| 17 | ⛔ 撤回 | 生产核实发现该清理任务早已存在，非问题（见上方「生产环境核实」） |

**注意**：复核 #16 时我在本地实际调用了该任务，它按设计发起了真实外呼并写库——本地 2 个导航站被标记为不显示（`Uninstalr` 返回 403、`Jenkins文档` 返回 500）。这正是每日「导航站拨测」的行为，未回滚，如需恢复 `is_show=True` 请告知。

### 第二轮：commit `55c3d86`（修复 #18–#22）

| # | 结论 | 实测证据 |
|---|------|----------|
| 18 | ✅ 有效 | 详情页 SQL 由 18 条降到 **13 条**：文章主查询 2→1 次（原先第 1、4 条是完全相同的 `slug` 查询），tags/keywords 预取各 2→1 次；302 路径不受影响（有主题文章仍 302、跟随目标 200）；重写 `get` 后浏览量仍是 A 首访 +1 / A 再访 +0 / B 首访 +1，无重复计数也无漏计 |
| 19 | ✅ 有效 | 映射改为延迟引用 `blog_tags` 常量构建；传入未注册的 sender 实测**不抛异常**且退化为清全部（4 个 key 全被清空）；`Tag/Category/MenuLink/ArticleComment/Subject` 五个 sender 均能命中各自映射 |
| 20 | ✅ 有效 | 详情页 18→13 条中，两条独立的 `COUNT(*) ... belong_id` 全部消失（改走 `comment_num` 注解）；页面渲染的「评论 N」与实际库值逐例一致（4 / 0 / 0 / 106），「N 人参与」= 库内去重人数（35）；未注解的实例仍能回退到实时 COUNT |
| 21 | ✅ 有效 | 事务内实测：新增 Subject 后只清 `blog_info`，`tag_list`/`category_list`/`menu_link` 三个 sentinel 全部保留 |
| 22 | ✅ 有效 | `logger.name == 'easytask.actions'`；`LOGGING['loggers']['easytask']` = `error_file`(TimedRotatingFileHandler) + `console`，`propagate=False`；按前缀规则 `easytask.actions` 命中该配置，生产（DEBUG=False、console 被 `require_debug_true` 过滤）下告警进 `log/izone-error.log` 而不再落到 lastResort/stderr |
| — | ✅ 无回归 | 93/93 模板编译通过；`manage.py check` 通过；16 个 URL 冒烟无 4xx/5xx；`DetailEditView`（另一套 queryset，未受注解影响）编辑页与草稿编辑页均 200；`comment_tags` 已在两个模板中 load |

### 第三轮：commit `9c30f5a`（修复 #23–#25 + 提交两项上线准备）

| 项 | 结论 | 实测证据 |
|----|------|----------|
| #23 协议配置单一来源 | ✅ 有效 | 全仓库现在只有 `settings.py:43` 一处读 `IZONE_PROTOCOL_HTTPS`；`ACCOUNT_DEFAULT_HTTP_PROTOCOL` / `PROTOCOL_HTTPS` / cookie 三处复用。取值与改动前**逐项一致**：默认 `PROTOCOL_HTTPS='http'`、`IS_HTTPS=False`、`ACCOUNT='http'`、`site_protocol()='http'`、cookies=False；`=https` 时全部翻转为 `'https'/True`；大写 `HTTPS` 也能正确识别 |
| Secure cookie 实际生效 | ✅ 有效 | **实测响应头**：`=https` 时 `sessionid.secure=True`，默认环境为空（不带标记）；两种环境下详情页仍 200 且浏览量 +1，说明开启后不影响计数 |
| #24 报告前提 | ✅ 有效 | 我独立复测：`check --deploy` 默认环境 **8 条**、带 `IZONE_PROTOCOL_HTTPS=https` **6 条**，与报告修正后的表述一致 |
| #25 迁移入库 | ✅ 有效 | `git ls-files` 已包含 `apps/easytask/migrations/0002_auto_20260911_1413.py`；`sqlmigrate easytask 0002` 只输出 `BEGIN/COMMIT` 与注释，**无任何 DDL**；`makemigrations --check` → "No changes detected" |
| 明文 HTTP 是否为可达路径 | ✅ 安全前提成立 | `http://tendcode.com/` 会 301 → https；直接以 HTTP 访问生产主机裸 IP，返回的是反向代理的默认欢迎页（无 Set-Cookie、不经 Django）。即不存在明文 HTTP 到达博客的路径，Secure 标记不会造成 cookie 丢失 |
| 是否有代码依赖 `request.is_secure()` | ✅ 无 | 全仓库无 `is_secure()` 调用，协议统一走 `PROTOCOL_HTTPS`；这也解释了为何本项目不需要 `SECURE_PROXY_SSL_HEADER`，以及为何 Secure 标记只认配置即可生效 |
| 无回归 | ✅ | `manage.py check` 通过；19 个 URL 冒烟无 4xx/5xx |

> **修复记录（2026-09-11，`--fix`）**：#23–#25 全部修复 —— `IZONE_PROTOCOL_HTTPS` 收敛为单一来源
> （顶部解析一次，allauth / sitemap / cookie 三处复用）、`check --deploy` 结论补上环境变量前提、
> 迁移文件随本次提交纳入版本控制。

## 工作区状态

- HEAD = `9c30f5a`，工作区干净；今天的 9 次提交（8 次改动 + 1 次安全/迁移提交）全部入库，共三轮修复均已实测复核。
- 未推送、未部署：生产仍运行 2026-09-06 的镜像，上线时把 `292318d..9c30f5a` 一起发。

---

## 备注

- 以下为已确认「无问题、不需改」的点：
  - 删除的 `summary.png` 只出现在 `migrations/0001_initial.py` 的历史 CharField 默认值里，当前模型已改为 `ProcessedImageField`；查库确认无任何记录引用该路径。
  - 删除的 `blog/js/mermaid/10.2.3/` 无引用；`blog/js/mermaid/11.4.1/mermaid.min.js` 存在，`scripts/detail.html` 指向 `blog/mermaid/9.4.0/` 的断链已被修正。
  - `action_check_friend_links` 从 `apps/easytask/actions.py` 删除是安全的：`tasks.py` 导入的是 `apps/easytask/action/friend_links.py` 中的同名函数。
  - `optimize_article_list` 与 `BaseDetailView.get_queryset` 的 `Count` 注解在 Django 2.2 下实测生成的 SQL 均为 `GROUP BY blog_article.id`，未退化为按全字段分组。
  - `ArticleListSerializer(exclude=('body',))` 实测生效：列表接口不含 `body`，详情接口仍返回 `body`。
  - `cache.delete_pattern` 在 `KEY_PREFIX="izone"` 下实测仍能正确删除。
  - `get_topics()` 预取的 `pub_articles` 是 list，模板只做遍历与真值判断，未调用 `.count()`，无 queryset/list 语义差异。
  - `Notification.get_p` 是外键（`instance.get_p_id` 成立）、`SystemNotification.get_p` 是 M2M（故走全量清缓存分支），`comment/signals.py` 的处理与模型一致。
  - `execute_task` 的 `finally` 中 `temp_script_path` 一定已赋值（在 `with` 块内），不存在 UnboundLocalError；该变量已无消费方。
  - 列表页 N+1 确已消除：`/` 第 1 页与第 2 页查询数同为 9；`/tags/` 4 条、`/subject/` 2 条、`/archive/` 4 条，均不随条目数增长。
  - `get_notifications_count` 缓存实测：首次 2 条查询、二次 0 条。
  - `get_parent_comments` 实测 6 条固定查询（父评论 + 作者社交账号 + 邮箱 + 子评论及其社交账号/邮箱），与评论条数无关（Django 2.2 允许对切片 queryset 做 prefetch，未抛异常）。
  - `feed:article:body:*` 缓存实测：首次写入、二次命中、内容一致。
  - `DetailEditView` 继承 `generic.DetailView`，不走 `BaseDetailView.get_queryset`，因此本轮新增的 `comment_num` 注解不影响编辑页。
  - 用户信息（`article.author`）的社交账号预取与 `user_avatar.html` 的访问路径一致；`get_user_link` 只在用户无社交账号时才访问 `emailaddress_set`，详情页已按此预取，无残留 N+1。
