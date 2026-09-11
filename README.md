# izone

一个以 Django 框架搭建的个人博客系统。

线上地址：https://tendcode.com/

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Django 2.2 + Python 3.9 |
| 数据库 | MySQL（utf8mb4） |
| 缓存 / 消息队列 | Redis |
| 异步任务 | Celery 4.4（Worker + Beat 合并单进程） |
| 搜索引擎 | MySQL FULLTEXT（n-gram 中文分词） |
| 前端 | Bootstrap 4 + jQuery |
| 容器化 | Docker + Gunicorn + Supervisord |

## 页面效果（响应式）

![PC首页](https://github.com/Hopetree/izone/assets/30201215/e221d09b-9921-4707-977d-95c263d282b6)

![PC首页暗色主题](https://github.com/Hopetree/izone/assets/30201215/ca505bfc-e5d0-40a1-b501-946975c03f73)

![PC文章页面](https://github.com/Hopetree/izone/assets/30201215/0c219bbd-6f29-4866-a827-6e98536f689a)

![PC 专题页，按文章归类](https://github.com/Hopetree/izone/assets/30201215/c0a828cc-2201-438b-a983-0c6c04a429c4)

![PC 友情链接页](https://github.com/Hopetree/izone/assets/30201215/033cdd61-75cf-41b4-bb45-9b45948daf3a)

![PC 在线工具](https://github.com/Hopetree/izone/assets/30201215/8336fd89-916b-49e5-94f2-a5a72e990158)

![ipad](https://user-images.githubusercontent.com/30201215/60588800-7e558800-9dca-11e9-8beb-5d2dcf01b869.jpg)

![iphone](https://user-images.githubusercontent.com/30201215/60588832-8e6d6780-9dca-11e9-84fa-f1d71510c81e.jpg)

## 文档索引

| 文档 | 说明 |
|------|------|
| [产品需求规格说明书](docs/design/01_PRD_产品需求规格说明书.md) | 产品需求，包含功能列表和非功能需求 |
| [架构设计文档](docs/design/02_TDD_架构设计文档.md) | 技术选型、模块划分、部署架构 |
| [数据库设计文档](docs/design/03_ERD_数据库设计文档.md) | 实体定义、关系说明、设计决策 |
| [API 接口文档](docs/design/04_API_接口文档.md) | 各应用 JSON API 端点 |
| [Code Review 报告](docs/code-review.md) | 代码审查与问题追踪 |
| [AGENTS.md](AGENTS.md) | 项目工作指南（架构速览、提交规范、构建约束） |

## 功能

- Django 后台管理系统，方便管理文章、用户及其他动态内容
- 文章分类、标签、专题（Subject → Topic → Article）层级结构
- 全文搜索（MySQL FULLTEXT n-gram 中文分词，直接查询实时数据）
- 文章评论系统（二级回复、微博表情、Markdown）、评论通知
- 用户认证（Django 用户系统 + OAuth 微博/GitHub 第三方登录）
- 浏览量统计（爬虫 UA 过滤、按访客 30 分钟去重、每日快照）
- 友链管理（在线申请、定时自动校链，外呼有并发上限）
- RSS 订阅、Sitemap 网站地图、百度 SEO 推送
- RESTful API（条件启用，DRF DefaultRouter；列表接口不返回正文）
- 在线工具（条件启用）、服务监控、导航网站、流程图、脚本工具分享
- 响应式设计（PC / iPad / 手机），暗色主题支持
- Redis 缓存（文章渲染/RSS 正文/站点配置/侧边栏统计/未读计数），Celery 定时任务调度

## 快速开始

### Docker 部署

```bash
# 构建镜像
docker build -t hopetree/izone:lts .

# slim 镜像（国内构建）
docker build --build-arg pip_index_url=http://mirrors.aliyun.com/pypi/simple/ \
             --build-arg pip_trusted_host=mirrors.aliyun.com \
             --build-arg debian_host=mirrors.ustc.edu.cn \
             -f Dockerfile-slim -t hopetree/izone:lts .

# 运行（需要预先启动 MySQL 和 Redis）
docker run -d \
  -e IZONE_MYSQL_HOST=mysql_host \
  -e IZONE_MYSQL_PASSWORD=your_password \
  -e IZONE_REDIS_HOST=redis_host \
  -p 8000:8000 \
  hopetree/izone:lts
```

### 本地开发

```bash
# 安装依赖
python -m venv env
source env/bin/activate
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver

# 启动 Celery（可选，异步任务需要；Worker 与 Beat 单进程）
celery -A izone worker -l info -B --pool=solo
```

## 环境变量

关键配置通过环境变量注入，完整列表见 [架构设计文档](docs/design/02_TDD_架构设计文档.md)。

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `IZONE_DEBUG` | 调试模式 | `True` |
| `IZONE_MYSQL_HOST` | MySQL 主机 | `127.0.0.1` |
| `IZONE_MYSQL_PASSWORD` | 数据库密码 | `python` |
| `IZONE_REDIS_HOST` | Redis 主机 | `127.0.0.1` |
| `IZONE_TOOL_FLAG` | 启用在线工具 | `True` |
| `IZONE_API_FLAG` | 启用 REST API | `True` |

## 项目结构

```
izone/
├── izone/              # Django 项目配置（settings/urls/wsgi）
├── apps/               # 所有 Django 应用
│   ├── blog/           # 核心博客应用
│   ├── oauth/          # 自定义用户模型 + OAuth 认证
│   ├── comment/        # 评论与通知系统
│   ├── easytask/       # Celery 异步任务
│   ├── api/            # REST API（条件启用）
│   ├── tool/           # 在线工具（条件启用）
│   ├── monitor/        # 服务监控
│   └── ...             # webstack, resume, flow, portinfo, rsshub
├── templates/          # 共享模板
├── utils/              # 共享工具（Markdown 扩展等）
├── docs/design/        # 设计文档
├── Dockerfile
└── manage.py
```

## 许可

[MIT License](LICENSE)

| — | 2026-07-24 | 根据 commit 2ca6b0b 更新：文档索引新增 Code Review 报告，功能列表新增脚本工具分享 |
| — | 2026-09-05 | 搜索切换为 MySQL FULLTEXT（移除 haystack/Whoosh）；Celery Worker 与 Beat 合并单进程；新增 AGENTS.md |
| — | 2026-09-11 | 浏览量改为按访客 30 分钟 Redis 去重；补充缓存清单与列表接口不返回正文；友链校链并发上限 |
