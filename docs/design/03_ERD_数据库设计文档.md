# 数据库设计文档（ERD）

> **项目名称**：izone（TendCode 个人博客）
> **最后更新**：2026-06-25

---

## 1. 实体关系总览

```
                    ┌──────────┐
                    │   Ouser  │ (用户)
                    └────┬─────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────┐   ┌──────────────┐
   │  Article │   │ Comment  │   │ Notification │
   └────┬─────┘   └────┬─────┘   └──────────────┘
        │               │
   ┌────┼────┬─────┐    └── parent/rep_to (自引用)
   │    │    │     │
   ▼    ▼    ▼     ▼
Category Tag Keyword Topic ─── Subject
```

---

## 2. 核心实体定义

### 2.1 用户认证（oauth 应用）

**Ouser**（继承 Django AbstractUser）
| 字段 | 类型 | 说明 |
|------|------|------|
| username | VARCHAR(150) | 用户名（继承） |
| email | VARCHAR(254) | 邮箱（继承） |
| password | VARCHAR(128) | 密码（继承） |
| link | URLField | 个人网址 |
| avatar | ImageField | 头像（django-imagekit 自动裁剪为 80x80） |

---

### 2.2 博客内容（blog 应用）

#### Article（文章）
| 字段 | 类型 | 说明 |
|------|------|------|
| author | FK → Ouser | 作者 |
| title | VARCHAR(150) | 文章标题 |
| summary | TEXT(230) | 摘要（SEO description） |
| body | TEXT | 文章内容（Markdown） |
| img_link | ImageField | 封面图（裁剪 250x150） |
| slug | SlugField (unique) | URL 标识符 |
| views | IntegerField | 浏览量 |
| is_top | BooleanField | 是否置顶 |
| is_publish | BooleanField | 是否发布 |
| category | FK → Category | 文章分类 |
| tags | M2M → Tag | 文章标签 |
| keywords | M2M → Keyword | SEO 关键词 |
| topic | FK → Topic (nullable) | 所属主题 |
| topic_order | IntegerField | 在主题中的排序 |
| topic_short_title | VARCHAR(50) | 主题内短标题 |
| create_date | DateTimeField | 创建时间（发布时重置为当前时间） |
| update_date | DateTimeField | 修改时间 |

#### Category（文章分类）
| 字段 | 类型 | 说明 |
|------|------|------|
| name | VARCHAR(20) | 分类名称 |
| slug | SlugField (unique) | URL 标识符 |
| description | TEXT(240) | 分类描述（SEO） |

#### Tag（文章标签）
| 字段 | 类型 | 说明 |
|------|------|------|
| name | VARCHAR(20) | 标签名称 |
| slug | SlugField (unique) | URL 标识符 |
| description | TEXT(240) | 标签描述（SEO） |

#### Keyword（SEO 关键词）
| 字段 | 类型 | 说明 |
|------|------|------|
| name | VARCHAR(20) | 关键词名称 |

#### Subject（专题）
| 字段 | 类型 | 说明 |
|------|------|------|
| name | VARCHAR(50) | 专题名称 |
| status | CHAR(20) | 状态：not_started / ongoing / completed |
| description | VARCHAR(250) | 专题描述 |
| sort_order | IntegerField | 排序权重 |
| cover_image | ImageField | 封面图（裁剪 250x150） |
| create_date | DateTimeField | 创建时间 |
| update_date | DateTimeField | 修改时间 |

#### Topic（专题下的主题/目录）
| 字段 | 类型 | 说明 |
|------|------|------|
| name | VARCHAR(50) | 主题名称 |
| subject | FK → Subject | 所属专题 |
| sort_order | IntegerField | 排序权重 |
| create_date | DateTimeField | 创建时间 |
| update_date | DateTimeField | 修改时间 |

**专题-主题-文章层级**：Subject → Topic → Article（一对多链式关系）

---

### 2.3 评论系统（comment 应用）

#### ArticleComment（文章评论）
| 字段 | 类型 | 说明 |
|------|------|------|
| author | FK → Ouser | 评论人 |
| belong | FK → Article | 所属文章 |
| content | TEXT | 评论内容 |
| user_agent | VARCHAR(255) | 解析后的 User-Agent |
| parent | FK → self (nullable) | 父评论（二级评论结构） |
| rep_to | FK → self (nullable) | 回复的目标评论 |
| create_date | DateTimeField | 创建时间 |

#### Notification（评论通知）
| 字段 | 类型 | 说明 |
|------|------|------|
| create_p | FK → Ouser | 通知触发者 |
| get_p | FK → Ouser | 通知接收者 |
| comment | FK → ArticleComment | 关联评论 |
| is_read | BooleanField | 是否已读 |
| create_date | DateTimeField | 通知时间 |

#### SystemNotification（系统通知）
| 字段 | 类型 | 说明 |
|------|------|------|
| title | VARCHAR(50) | 通知标题 |
| content | TEXT | 通知内容（HTML） |
| get_p | M2M → Ouser | 收信人（多对多） |
| is_read | BooleanField | 是否已读 |
| create_date | DateTimeField | 推送时间 |

---

### 2.4 其他重要实体（blog 应用）

#### FriendLink（友情链接）
| 字段 | 类型 | 说明 |
|------|------|------|
| name | VARCHAR(50) | 网站名称 |
| description | VARCHAR(100) | 网站描述 |
| link | URLField | 友链地址 |
| logo | ImageField | 网站 Logo（裁剪 120x120） |
| is_active | BooleanField | 是否有效 |
| is_show | BooleanField | 是否展示 |
| not_show_reason | VARCHAR(50) | 禁用原因 |
| create_date | DateTimeField | 创建时间 |

#### Timeline（时间线）
| 字段 | 类型 | 说明 |
|------|------|------|
| title | VARCHAR(100) | 标题 |
| content | TEXT | 主要内容 |
| side | CHAR(1) | 位置：L（左）/ R（右） |
| star_num | IntegerField | 重要性：1-5 星 |
| icon | VARCHAR(50) | Font Awesome 图标类名 |
| icon_color | VARCHAR(20) | 图标颜色 |
| update_date | DateTimeField | 更新时间 |

#### PageView（单页面浏览量）
| 字段 | 类型 | 说明 |
|------|------|------|
| url | VARCHAR(255) (unique) | 页面地址 |
| name | VARCHAR(255) | 页面名称 |
| views | IntegerField | 浏览量 |
| is_compute | BooleanField | 是否计入总量统计 |

#### ArticleView（每日访问统计快照）
| 字段 | 类型 | 说明 |
|------|------|------|
| date | VARCHAR(10) (unique) | 统计日期（格式 YYYYMMDD） |
| body | TEXT (JSON) | 统计数据（总量/文章/页面/每小时分布） |

#### FeedHub（RSS 源聚合）
| 字段 | 类型 | 说明 |
|------|------|------|
| name | VARCHAR(50) (unique) | 源名称 |
| url | VARCHAR(255) | Feed 地址 |
| icon | TEXT | 图标（Base64 或 URL） |
| is_active | BooleanField | 是否采集 |
| data | TEXT (JSON) | 采集到的 feed 数据 |
| sort_order | IntegerField | 排序 |

#### SiteConfig（网站配置 - 单例模式）
| 字段 | 类型 | 说明 |
|------|------|------|
| config_data | TEXT (JSON) | 全站配置（覆盖 settings.py 默认值） |

#### Note（便签笔记）
| 字段 | 类型 | 说明 |
|------|------|------|
| title | VARCHAR(200) | 标题 |
| content | TEXT | 内容 |
| tags | VARCHAR(200) | 标签（逗号分隔） |
| is_publish | BooleanField | 是否发布 |

#### Fitness（健身数据）
| 字段 | 类型 | 说明 |
|------|------|------|
| location | VARCHAR(50) | 位置 |
| run_date | DateTimeField | 跑步时间 |
| distance | FloatField | 距离（公里） |
| training_duration | VARCHAR(7) | 训练时长 |
| average_pace | VARCHAR(7) | 平均配速 |
| average_heart_rate | IntegerField | 平均心率 |
| average_cadence | IntegerField | 平均步频 |
| five_pace / five_heart_rate / five_power / five_cadence | VARCHAR(50) | 5 段分段数据 |
| heart_rate | VARCHAR(50) | 心率区间分布 |

#### Project（个人项目）
| 字段 | 类型 | 说明 |
|------|------|------|
| name | VARCHAR(50) | 项目名称 |
| description | VARCHAR(250) | 项目描述 |
| link | URLField | 跳转地址 |
| cover_image | ImageField | 封面图 |
| sort_order | IntegerField | 排序 |

#### 辅助模型
| 模型 | 说明 |
|------|------|
| Carousel | 首页轮播图（number/排序, img_url, url） |
| Silian | 死链记录（badurl, remark） |
| AboutBlog | About 页面内容（body - Markdown） |
| MenuLink | 导航栏外链（name/icon/link/sort_order） |

---

### 2.5 其他应用实体

#### MonitorServer（monitor 应用）
| 字段 | 类型 | 说明 |
|------|------|------|
| name | VARCHAR(30) (unique) | 服务器名称 |
| interval | IntegerField | 上报间隔（秒） |
| username / password / push_url | - | 客户端认证信息 |
| secret_key / secret_value | - | AES 加密凭证（自动生成） |
| data | TEXT (JSON) | 上报数据 |
| active / alarm | BooleanField | 是否有效 / 是否告警 |

#### TaskScript / EnvironmentVariable（easytask 应用）
| 字段 | 类型 | 说明 |
|------|------|------|
| name | VARCHAR(255) (unique) | 脚本名称 |
| script | TEXT | Python/Shell 代码 |
| script_type | CHAR(10) | python / shell |
| — | — | — |
| key | VARCHAR(255) (unique) | 环境变量名 |
| value | TEXT | 环境变量值 |

---

### 2.6 脚本分享（scripts 应用）

#### Script（脚本）
| 字段 | 类型 | 说明 |
|------|------|------|
| title | VARCHAR(150) | 标题 |
| slug | SlugField (unique) | URL 标识符 |
| description | TEXT | 说明文档（Markdown） |
| code | TEXT | 脚本代码 |
| script_type | CHAR(10) | 脚本类型：shell / python |
| filename | VARCHAR(100) | 下载文件名（如 install-docker.sh） |
| run_cmd | VARCHAR(500) | 下载后的执行命令 |
| is_publish | BooleanField | 是否发布（仅已发布可通过公开端点下载） |
| create_date | DateTimeField | 创建时间 |
| update_date | DateTimeField | 修改时间 |

**说明**：Script 为独立实体，无外键关联。通过 `full_command` 属性动态拼接 `curl -o {filename} {raw_url} && {run_cmd}` 一键命令。公开下载端点仅返回 `is_publish=True` 的脚本内容。

---

## 3. 关键数据库设计决策

### 3.1 不使用外键时区（USE_TZ = False）
所有时间存储为本地时间（Asia/Shanghai），避免 MySQL 时区转换问题。

### 3.2 utf8mb4 字符集
数据库连接使用 `utf8mb4` 编码，支持 emoji 等 4 字节 Unicode 字符。

### 3.3 ArticleView 使用 JSON 存储每日统计
每日访问统计数据以 JSON 格式存储在 `body` 字段中，包含：
- `total_views_num` / `article_views_num` / `page_views_num`：总量统计
- `article_views`：每篇文章浏览量字典 `{article_id: views}`
- `page_views`：每个页面浏览量字典 `{url: views}`
- `article_every_hours` / `page_every_hours`：每小时访问量 `{"00": N, "01": N, ...}`

### 3.4 SiteConfig 单例模式
`SiteConfig` 的 `save()` 方法强制仅允许一条记录存在，存储全站配置 JSON，作为 `settings.py` 环境变量配置的运行时替代方案。

### 3.5 MonitorServer 加密凭证
`username` / `password` / `push_url` 通过 AES 加密后存储在 `secret_value` 中，`secret_key` 为自动生成的 32 位随机密钥。

### 3.6 评论模型使用抽象基类
`Comment` 为抽象基类，`ArticleComment` 继承并添加 `belong`（FK→Article）关系，便于扩展（如未来添加其他类型的评论）。

| — | 2026-07-24 | 根据 commit 2ca6b0b 更新：新增 2.6 Script 实体定义（scripts 应用） |
