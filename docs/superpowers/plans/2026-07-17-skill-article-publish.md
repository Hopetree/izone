# Skill 文章发布系统 - 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 开发后端 API + Claude Code Skill，实现通过 AI 对话快速发布文章到博客。

**Architecture:** 后端新增两个 skill 专用 API 端点（meta 聚合查询 + publish 发布），前端 Skill 文件作为 Claude Code 指令集，AI 负责解析 markdown、匹配已有数据、组装 payload 调用 API。

**Tech Stack:** Django 2.2, DRF, rest_framework.authtoken, Python 3.9, Bash/curl

**Spec:** [docs/superpowers/specs/2026-07-16-skill-article-publish-design.md](../specs/2026-07-16-skill-article-publish-design.md)

## Global Constraints

- API 路径挂载在 `/openapi/v1/skill/` 下
- Token 认证用于整套 REST API，在 Django Admin 管理
- Category/Tag 按 name 查询用 `.filter().first()`（name 非 unique）
- Topic 不允许自动创建
- `is_publish` 默认 `false`（草稿），`img_link` 不传
- 错误响应统一 `{"success": false, "error": "中文描述"}`

---

## File Map

| 文件 | 操作 | 职责 |
|------|------|------|
| `izone/settings.py:43,64,223-229` | 修改 | 加 `rest_framework.authtoken` + TokenAuthentication |
| `apps/api/serializers.py` | 修改 | 新增 `ArticlePublishSerializer` |
| `apps/api/views.py` | 修改 | 改 ArticleListSet 权限；新增 `SkillMetaView`、`SkillPublishView` |
| `apps/api/urls.py` | 修改 | 新增 skill 专用路由 |
| `.claude/skills/publish-article.md` | 创建 | Skill 指令文件（AI 执行发布流程的操作手册） |
| `.claude/skill-publish.json` | 创建 | Skill 配置文件（api_base, token, 默认分类等） |

---

### Task 1: 配置 Token 认证

**Files:**
- Modify: `izone/settings.py:43-77` (INSTALLED_APPS)
- Modify: `izone/settings.py:223-229` (REST_FRAMEWORK)

**Interfaces:**
- Produces: `rest_framework.authtoken` 已安装，`TokenAuthentication` 作为全局默认认证

---

- [ ] **Step 1: 添加 `rest_framework.authtoken` 到 INSTALLED_APPS**

在 `izone/settings.py` 第 64 行 `'rest_framework',` 之后添加：

```python
    'rest_framework.authtoken',  # DRF Token 认证
```

---

- [ ] **Step 2: 配置 TokenAuthentication 为默认认证**

修改 `izone/settings.py` 第 223-229 行的 `REST_FRAMEWORK` 配置：

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20
}
```

---

- [ ] **Step 3: 运行 migrate 创建 Token 表**

```bash
cd ~/izone && source env/bin/activate && python manage.py migrate
```

---

- [ ] **Step 4: 提交**

```bash
git add izone/settings.py
git commit -m "feat(api): 配置 DRF TokenAuthentication 全局认证

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: 调整 ArticleListSet 权限

**Files:**
- Modify: `apps/api/views.py:26-40`

**Interfaces:**
- Consumes: TokenAuthentication 已全局配置（Task 1）
- Produces: ArticleListSet 使用 `IsAuthenticated` 替代 `IsAdminUser`，`authentication_classes` 使用全局默认（不再单独指定）

---

- [ ] **Step 1: 修改 ArticleListSet 权限和认证**

修改 `apps/api/views.py` 第 26-40 行：

```python
class ArticleListSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    # 使用全局认证方案（TokenAuthentication + SessionAuthentication + BasicAuthentication）
    # 不再单独指定 authentication_classes
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        # 仅返回 is_publish=True 的数据
        return Article.objects.filter(is_publish=True)
```

注意：在文件顶部需要确保 `from rest_framework import permissions` 存在。当前 views.py 第 5 行已有 `from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly, IsAdminUser`，将其替换为 `from rest_framework import permissions`。

---

- [ ] **Step 2: 提交**

```bash
git add apps/api/views.py
git commit -m "feat(api): ArticleListSet 权限调整为 IsAuthenticated，支持 Token 认证

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: 创建 SkillMetaView（聚合元数据查询）

**Files:**
- Modify: `apps/api/serializers.py` (末尾追加)
- Modify: `apps/api/views.py` (末尾追加)
- Modify: `apps/api/urls.py`

**Interfaces:**
- Consumes: TokenAuthentication（Task 1），Category/Tag/Topic 模型
- Produces: `GET /openapi/v1/skill/meta/` → `{"categories": [...], "tags": [...], "topics": [...]}`

---

- [ ] **Step 1: 新增 serializers**

在 `apps/api/serializers.py` 末尾追加：

```python
class SkillCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description')


class SkillTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'description')


class SkillTopicSerializer(serializers.ModelSerializer):
    subject_id = serializers.ReadOnlyField(source='subject.id')
    subject_name = serializers.ReadOnlyField(source='subject.name')
    subject_status = serializers.ReadOnlyField(source='subject.status')

    class Meta:
        model = Topic
        fields = ('id', 'name', 'subject_id', 'subject_name', 'subject_status')
```

---

- [ ] **Step 2: 新增 SkillMetaView**

在 `apps/api/views.py` 末尾追加：

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from blog.models import Category, Tag, Topic
from .serializers import SkillCategorySerializer, SkillTagSerializer, SkillTopicSerializer


class SkillMetaView(APIView):
    """聚合返回分类、标签、主题列表，供 skill 匹配决策"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        tags = Tag.objects.all()
        topics = Topic.objects.select_related('subject').all()

        return Response({
            'categories': SkillCategorySerializer(categories, many=True).data,
            'tags': SkillTagSerializer(tags, many=True).data,
            'topics': SkillTopicSerializer(topics, many=True).data,
        })
```

---

- [ ] **Step 3: 配置 skill URL 路由**

修改 `apps/api/urls.py`：

```python
# -*- coding:utf-8 -*-
# @Date  : 2019/2/1

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (UserListSet, ArticleListSet, TagListSet,
                    CategoryListSet, TimelineListSet,
                    ToolLinkListSet, NavigationSiteListSet,
                    SkillMetaView, SkillPublishView)

router = DefaultRouter()
# router.register(r'users', UserListSet)
router.register(r'articles', ArticleListSet)
router.register(r'tags', TagListSet)
router.register(r'categorys', CategoryListSet)
router.register(r'timelines', TimelineListSet)
router.register(r'toollinks', ToolLinkListSet)
router.register(r'navigation', NavigationSiteListSet)

# Skill 专用路由（独立于 DefaultRouter）
skill_urlpatterns = [
    path('skill/meta/', SkillMetaView.as_view(), name='skill-meta'),
    # path('skill/articles/publish/', SkillPublishView.as_view(), name='skill-publish'),  # Task 4 启用
]
```

---

- [ ] **Step 4: 在主 URL 配置中挂载 skill 路由**

修改 `izone/urls.py` 第 53-57 行，在 API 条件块中加入 skill 路由：

```python
if settings.API_FLAG:
    from api.urls import router, skill_urlpatterns

    urlpatterns.append(path('openapi/v1/', include((router.urls, router.root_view_name),
                                               namespace='api')))  # restframework
    urlpatterns.append(path('openapi/v1/', include((skill_urlpatterns, 'skill'))))
```

---

- [ ] **Step 5: 手动测试 meta 接口**

```bash
# 先确保有 Token（后面 Task 5 会正式创建，这里用 manage.py 临时测试）
cd ~/izone && source env/bin/activate
python manage.py shell -c "
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.first()
token, _ = Token.objects.get_or_create(user=user)
print(token.key)
"
```

记下 token，然后：

```bash
curl -H "Authorization: Token <your-token>" http://127.0.0.1:8000/openapi/v1/skill/meta/ | python -m json.tool
```

预期：返回 200，包含 `categories`、`tags`、`topics` 三个数组。

---

- [ ] **Step 6: 提交**

```bash
git add apps/api/serializers.py apps/api/views.py apps/api/urls.py izone/urls.py
git commit -m "feat(api): 新增 SkillMetaView 聚合元数据查询接口

GET /openapi/v1/skill/meta/ 返回分类、标签、主题列表

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: 创建 SkillPublishView（文章发布接口）

**Files:**
- Modify: `apps/api/serializers.py` (末尾追加)
- Modify: `apps/api/views.py` (末尾追加)
- Modify: `apps/api/urls.py`

**Interfaces:**
- Consumes: TokenAuthentication（Task 1），Article/Category/Tag/Keyword/Topic 模型
- Produces: `POST /openapi/v1/skill/articles/publish/` → `{"success": true, "id": 42, "url": "...", "title": "..."}`

---

- [ ] **Step 1: 新增 ArticlePublishSerializer**

在 `apps/api/serializers.py` 末尾追加：

```python
from blog.models import Article, Keyword


class CategoryField(serializers.DictField):
    """分类字段：接收 {name, slug, description}"""
    child = serializers.CharField()


class TagItemField(serializers.DictField):
    """标签字段：接收 {name, slug, description}"""
    child = serializers.CharField()


class TopicField(serializers.DictField):
    """主题字段：接收 {id?, name?}"""
    child = serializers.CharField(required=False)


class ArticlePublishSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=150, required=True)
    slug = serializers.SlugField(max_length=50, required=True)
    body = serializers.CharField(required=True)
    summary = serializers.CharField(max_length=230, required=True)
    is_publish = serializers.BooleanField(default=False)
    is_top = serializers.BooleanField(default=False)
    category = CategoryField(required=True)
    tags = serializers.ListField(child=TagItemField(), required=False, default=list)
    keywords = serializers.ListField(child=serializers.CharField(max_length=20), required=False, default=list)
    topic = TopicField(required=False, allow_null=True, default=None)
    topic_order = serializers.IntegerField(required=False, default=99)
    topic_short_title = serializers.CharField(max_length=50, required=False, allow_blank=True, default='')

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("标题不能为空")
        if len(value) > 150:
            raise serializers.ValidationError(f"标题长度不能超过 150 字符，当前 {len(value)} 字符")
        return value.strip()

    def validate_slug(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("slug 不能为空")
        if Article.objects.filter(slug=value).exists():
            existing = Article.objects.get(slug=value)
            raise serializers.ValidationError(
                f"slug '{value}' 已被文章 '{existing.title}' 使用，请更换"
            )
        return value.strip()

    def validate_body(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("文章正文不能为空")
        return value

    def validate_summary(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("文章摘要不能为空")
        if len(value) > 230:
            raise serializers.ValidationError(f"摘要长度不能超过 230 字符，当前 {len(value)} 字符")
        return value.strip()

    def validate_category(self, value):
        name = value.get('name', '').strip()
        slug = value.get('slug', '').strip()
        if not name:
            raise serializers.ValidationError("category.name 为必填项")
        if len(name) > 20:
            raise serializers.ValidationError(f"分类名长度不能超过 20 字符，当前 {len(name)} 字符")
        if not slug:
            raise serializers.ValidationError("category.slug 为必填项")
        if len(slug) > 50:
            raise serializers.ValidationError(f"分类 slug 长度不能超过 50 字符")
        if Category.objects.filter(slug=slug).exists():
            # 检查是否是同名分类（允许同 name 复用），否则拒绝
            existing = Category.objects.filter(name=name).first()
            if not existing or existing.slug != slug:
                raise serializers.ValidationError(
                    f"分类 slug '{slug}' 已被占用"
                )
        return {'name': name, 'slug': slug, 'description': value.get('description', '分类描述').strip()}

    def validate_tags(self, value):
        cleaned = []
        for tag in value:
            name = tag.get('name', '').strip()
            slug = tag.get('slug', '').strip()
            if not name:
                raise serializers.ValidationError("tag.name 为必填项")
            if len(name) > 20:
                raise serializers.ValidationError(f"标签名 '{name}' 长度不能超过 20 字符，当前 {len(name)} 字符")
            if not slug:
                raise serializers.ValidationError("tag.slug 为必填项")
            if len(slug) > 50:
                raise serializers.ValidationError(f"标签 '{name}' slug 长度不能超过 50 字符")
            # 检查 slug 冲突（非同名标签的情况）
            existing = Tag.objects.filter(name=name).first()
            if not existing and Tag.objects.filter(slug=slug).exists():
                raise serializers.ValidationError(
                    f"标签 slug '{slug}' 已被占用"
                )
            cleaned.append({
                'name': name,
                'slug': slug,
                'description': tag.get('description', '标签描述').strip(),
            })
        return cleaned

    def validate_topic(self, value):
        if value is None:
            return None
        topic_id = value.get('id')
        topic_name = value.get('name', '').strip()

        if topic_id:
            try:
                return Topic.objects.get(pk=int(topic_id))
            except (Topic.DoesNotExist, ValueError):
                pass

        if topic_name:
            topic = Topic.objects.filter(name=topic_name).first()
            if topic:
                return topic

        # topic 不存在，列出可用的
        available = Topic.objects.values_list('name', flat=True)[:20]
        available_list = '、'.join(available) if available else '(无)'
        raise serializers.ValidationError(
            f"主题 '{topic_name or topic_id}' 不存在，可用主题: {available_list}"
        )

    def create(self, validated_data):
        request = self.context['request']
        category_data = validated_data.pop('category')
        tags_data = validated_data.pop('tags', [])
        keywords_data = validated_data.pop('keywords', [])
        topic = validated_data.pop('topic', None)

        # 处理 category: get-or-create + 更新描述
        category_name = category_data['name']
        category = Category.objects.filter(name=category_name).first()
        if category:
            new_desc = category_data.get('description', '')
            if new_desc and new_desc != category.description and new_desc != '分类描述':
                category.description = new_desc
                category.save(update_fields=['description'])
        else:
            slug = category_data['slug']
            if Category.objects.filter(slug=slug).exists():
                conflict = Category.objects.get(slug=slug)
                raise serializers.ValidationError(
                    f"分类 '{category_name}' 不存在，尝试创建时 slug '{slug}' 已被分类 '{conflict.name}' 占用"
                )
            category = Category.objects.create(
                name=category_name,
                slug=slug,
                description=category_data.get('description', '分类描述'),
            )

        # 处理 tags: get-or-create + 更新描述
        tag_objects = []
        for tag_data in tags_data:
            tag_name = tag_data['name']
            tag = Tag.objects.filter(name=tag_name).first()
            if tag:
                new_desc = tag_data.get('description', '')
                if new_desc and new_desc != tag.description and new_desc != '标签描述':
                    tag.description = new_desc
                    tag.save(update_fields=['description'])
            else:
                slug = tag_data['slug']
                if Tag.objects.filter(slug=slug).exists():
                    conflict = Tag.objects.get(slug=slug)
                    raise serializers.ValidationError(
                        f"标签 '{tag_name}' 不存在，尝试创建时 slug '{slug}' 已被标签 '{conflict.name}' 占用"
                    )
                tag = Tag.objects.create(
                    name=tag_name,
                    slug=slug,
                    description=tag_data.get('description', '标签描述'),
                )
            tag_objects.append(tag)

        # 处理 keywords: get-or-create
        keyword_objects = []
        for kw_name in keywords_data:
            kw, _ = Keyword.objects.get_or_create(name=kw_name.strip())
            keyword_objects.append(kw)

        # 创建文章
        article = Article.objects.create(
            author=request.user,
            title=validated_data['title'],
            slug=validated_data['slug'],
            body=validated_data['body'],
            summary=validated_data['summary'],
            is_publish=validated_data.get('is_publish', False),
            is_top=validated_data.get('is_top', False),
            category=category,
            topic=topic,
            topic_order=validated_data.get('topic_order', 99),
            topic_short_title=validated_data.get('topic_short_title', '') or '',
        )
        article.tags.set(tag_objects)
        article.keywords.set(keyword_objects)

        return article
```

---

- [ ] **Step 2: 新增 SkillPublishView**

在 `apps/api/views.py` 末尾追加：

```python
class SkillPublishView(APIView):
    """Skill 专用文章发布接口"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ArticlePublishSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            # 提取第一个错误信息
            errors = serializer.errors
            first_field = next(iter(errors))
            first_error = errors[first_field]
            if isinstance(first_error, list):
                msg = first_error[0]
            elif isinstance(first_error, dict):
                # 嵌套错误（如 category 内部字段）
                nested_field = next(iter(first_error))
                msg = f"{first_field}.{nested_field}: {first_error[nested_field][0]}"
            else:
                msg = str(first_error)
            return Response({'success': False, 'error': msg}, status=400)

        try:
            article = serializer.save()
            return Response({
                'success': True,
                'id': article.id,
                'url': article.get_absolute_url(),
                'title': article.title,
            }, status=201)
        except serializers.ValidationError as e:
            return Response({'success': False, 'error': str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)}, status=400)
        except Exception as e:
            return Response({'success': False, 'error': f'创建文章失败: {str(e)}'}, status=500)
```

---

- [ ] **Step 3: 启用 skill publish 路由**

修改 `apps/api/urls.py`，取消 Task 3 中注释的路由：

```python
skill_urlpatterns = [
    path('skill/meta/', SkillMetaView.as_view(), name='skill-meta'),
    path('skill/articles/publish/', SkillPublishView.as_view(), name='skill-publish'),
]
```

---

- [ ] **Step 4: 手动测试 publish 接口**

```bash
# 启动开发服务器
cd ~/izone && source env/bin/activate && python manage.py runserver &

# 测试发布文章
curl -X POST http://127.0.0.1:8000/openapi/v1/skill/articles/publish/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试文章",
    "slug": "test-article-001",
    "body": "## 这是一篇测试文章\n\n正文内容。",
    "summary": "这是一篇测试文章的摘要，用于验证 API 是否正常工作。",
    "is_publish": false,
    "is_top": false,
    "category": {"name": "技术", "slug": "tech", "description": "技术相关文章"},
    "tags": [{"name": "Test", "slug": "test", "description": "测试标签"}],
    "keywords": ["测试"]
  }' | python -m json.tool
```

预期：返回 201，包含 `success: true`、`id`、`url`、`title`。

---

- [ ] **Step 5: 测试错误场景**

```bash
# 测试 1: slug 冲突
curl -X POST http://127.0.0.1:8000/openapi/v1/skill/articles/publish/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "重复slug",
    "slug": "test-article-001",
    "body": "正文",
    "summary": "摘要",
    "category": {"name": "技术", "slug": "tech", "description": "技术"}
  }'
# 预期: {"success": false, "error": "slug 'test-article-001' 已被文章 '测试文章' 使用，请更换"}

# 测试 2: 不存在的主题
curl -X POST http://127.0.0.1:8000/openapi/v1/skill/articles/publish/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试主题",
    "slug": "test-topic-001",
    "body": "正文",
    "summary": "摘要",
    "category": {"name": "技术", "slug": "tech2", "description": "技术"},
    "topic": {"name": "不存在的主题"}
  }'
# 预期: {"success": false, "error": "主题 '不存在的主题' 不存在，可用主题: ..."}

# 测试 3: 标题为空
curl -X POST http://127.0.0.1:8000/openapi/v1/skill/articles/publish/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "", "slug": "x", "body": "x", "summary": "x", "category": {"name": "技术", "slug": "tech3", "description": "x"}}'
# 预期: {"success": false, "error": "标题不能为空"}
```

---

- [ ] **Step 6: 删除测试文章（清理数据库）**

```bash
cd ~/izone && source env/bin/activate
python manage.py shell -c "
from blog.models import Article
Article.objects.filter(slug__startswith='test-').delete()
print('Cleaned up test articles')
"
```

---

- [ ] **Step 7: 提交**

```bash
git add apps/api/serializers.py apps/api/views.py apps/api/urls.py
git commit -m "feat(api): 新增 SkillPublishView 文章发布接口

POST /openapi/v1/skill/articles/publish/
- 字段校验（标题/slug/正文/摘要 必填）
- Category/Tag 按 name get-or-create，支持描述更新
- Keyword 按 name get-or-create
- Topic 仅查不建，不存在返回可用列表
- 统一错误格式 {success, error}

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 5: 在 Admin 中为用户生成 Token

**Files:**
- Create: (无，使用 manage.py shell)

**Interfaces:**
- Produces: 用户拥有 Token，可在后台查看和管理

---

- [ ] **Step 1: 为用户生成 Token**

```bash
cd ~/izone && source env/bin/activate
python manage.py shell -c "
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
User = get_user_model()

# 列出所有用户
for u in User.objects.filter(is_staff=True):
    token, created = Token.objects.get_or_create(user=u)
    status = '新建' if created else '已存在'
    print(f'{status}: {u.username} -> {token.key[:10]}...')
"
```

---

- [ ] **Step 2: 验证 Admin 中可查看 Token**

启动 `python manage.py runserver`，访问 `http://127.0.0.1:8000/adminx/authtoken/token/`，确认可以看到 Token 列表。

（无需提交，这是运维操作）

---

### Task 6: 创建 Skill 配置文件

**Files:**
- Create: `.claude/skill-publish.json`

**Interfaces:**
- Consumes: Token（Task 5 获取）
- Produces: Skill 配置文件，供 AI 读取

---

- [ ] **Step 1: 创建配置模板文件**

创建 `.claude/skill-publish.json`：

```json
{
  "api_base": "http://127.0.0.1:8000/openapi/v1",
  "token": "将你的 Token 填入这里",
  "default_category": {
    "name": "技术",
    "slug": "tech",
    "description": "技术相关文章"
  },
  "preferred_tags": [
    { "name": "Python", "slug": "python", "description": "Python 编程语言" },
    { "name": "Django", "slug": "django", "description": "Django Web 框架" }
  ]
}
```

---

- [ ] **Step 2: 将配置文件加入 .gitignore（如果尚未忽略）**

检查 `.claude/` 是否已在 `.gitignore` 中。如果不在，添加：

```bash
grep -q '^\.claude/' .gitignore || echo '.claude/' >> .gitignore
```

注：`skill-publish.json` 包含敏感 token，不应提交到 git。

---

- [ ] **Step 3: 提交**

```bash
# 只提交 .gitignore 变更（如果有）
git add .gitignore 2>/dev/null && git commit -m "chore: .claude/ 加入 .gitignore" || echo "No changes to commit"
```

---

### Task 7: 创建 Skill 指令文件

**Files:**
- Create: `.claude/skills/publish-article.md`

**Interfaces:**
- Consumes: `.claude/skill-publish.json` 配置文件，`GET /skill/meta/` API，`POST /skill/articles/publish/` API
- Produces: Claude Code 可识别的 skill，用户输入 `/publish-article` 或 "发布文章" 触发

---

- [ ] **Step 1: 创建 Skill 指令文件**

创建 `.claude/skills/publish-article.md`：

````markdown
---
name: publish-article
description: 发布文章到博客。支持从本地 markdown 文件或直接粘贴内容，AI 自动解析、匹配分类/标签、确认后发布。
metadata:
  type: project
---

# 文章发布 Skill

## 配置

发布前必须先读取 `.claude/skill-publish.json` 获取以下配置：
- `api_base`: API 地址（末尾无斜杠）
- `token`: 认证 Token
- `default_category`: 默认分类（可选，包含 name、slug、description）
- `preferred_tags`: 常用标签列表（可选）

## 发布流程

### 1. 获取文章内容

用户提供 markdown 文件路径或直接粘贴内容。如果是文件路径，使用 Read 工具读取。

### 2. 解析文章内容（遵守字段约束）

| 字段 | 约束 | 生成方式 |
|------|------|----------|
| `title` | ≤150 字符 | 从第一个 `# 标题` 提取 |
| `slug` | ≤50 字符 | 英文翻译/音译标题，小写，空格→连字符，去掉特殊字符 |
| `summary` | ≤230 字符 | 总结文章核心内容，非简单截取 |
| `body` | markdown 原文 | 不做修改 |
| `is_publish` | 默认 `false` | 存草稿 |
| `is_top` | 默认 `false` | 除非用户明确说"置顶" |
| `img_link` | 不传 | 使用默认图片 |

### 3. 查询已有分类/标签/主题

```bash
curl -s -H "Authorization: Token <token>" "<api_base>/skill/meta/"
```

从返回的 JSON 中获取：
- `categories`: 已有分类列表（id, name, slug, description）
- `tags`: 已有标签列表（id, name, slug, description）
- `topics`: 已有主题列表（id, name, subject_id, subject_name, subject_status）

### 4. 匹配决策

**分类**：
- 优先使用配置文件中的 `default_category`
- 否则根据文章内容推断，与已有分类的 name 进行匹配
- 匹配不到则询问用户，或生成新的分类信息

**标签**：
- 优先匹配配置文件中的 `preferred_tags` + 已有标签
- 根据文章内容提取关键词，与已有标签 name 匹配
- 已匹配到的：复用已有信息（name、slug、description），如果原 description 是占位符（"标签描述"）或不够清晰，AI 生成更好的描述
- 匹配不到的：AI 生成完整的 name（≤20）、slug（≤50）、description（≤240）

**主题**：
- 根据文章内容匹配已有主题（从 meta 查询结果中找）
- 匹配不到则不设置

> 对于已匹配到的分类和标签：如果其 description 是默认占位符（"分类描述"/"标签描述"）或明显不相关，AI 应生成更好的描述传入，接口会自动更新。

### 5. 展示确认信息

一次性展示所有解析结果，等待用户确认：

```
我解析了这篇文章，请确认以下信息：

📝 标题: 《xxx》 (xx字符)
🔗 Slug: xxx
📂 分类: xxx（已有/新建）
🏷️ 标签: xxx（已有）, xxx（新建）
📖 主题: xxx → xxx（状态）(如无可省略)
📌 置顶: 否
📄 摘要: xxx... (xx字符)
📝 状态: 存为草稿

确认提交吗？或告诉我要调整的地方。
```

### 6. 发布文章

用户确认后，调用 API：

```bash
curl -s -X POST -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '<JSON_PAYLOAD>' \
  "<api_base>/skill/articles/publish/"
```

JSON payload 结构：

```json
{
  "title": "...",
  "slug": "...",
  "body": "...",
  "summary": "...",
  "is_publish": false,
  "is_top": false,
  "category": {"name": "...", "slug": "...", "description": "..."},
  "tags": [{"name": "...", "slug": "...", "description": "..."}],
  "keywords": ["..."],
  "topic": {"id": 1, "name": "..."},
  "topic_order": 99,
  "topic_short_title": ""
}
```

### 7. 处理响应

**成功**（HTTP 201）：
```
✅ 文章已保存为草稿！
预览地址: <api_base 的域名部分 + url>
可在后台设置发布状态。
```

**失败**（HTTP 400/500）：
- `slug 冲突` → 换一个 slug 重新发布（自动，不需要用户干预）
- `分类/标签 slug 冲突` → 调整 slug 后重试
- `主题不存在` → 展示可用主题列表，询问用户
- `字段校验失败` → 根据错误描述修正后重试
- 其他错误 → 展示给用户，询问如何处理

### 8. 错误重试策略

- slug 冲突: 最多自动重试 3 次，每次在 slug 末尾追加数字（如 `my-slug-2`、`my-slug-3`）
- 超过 3 次仍冲突: 展示给用户，请用户手动指定 slug
````

---

- [ ] **Step 2: 提交**

```bash
git add .claude/skills/publish-article.md
git commit -m "feat(skill): 创建文章发布 Skill 指令文件

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 8: 端到端验证

**Files:**
- (无，验证流程)

**Interfaces:**
- Consumes: 所有 Task 1-7 的产出

---

- [ ] **Step 1: 启动开发服务器**

```bash
cd ~/izone && source env/bin/activate && python manage.py runserver &
```

---

- [ ] **Step 2: 端到端测试 — meta 查询 + publish 发布**

```bash
TOKEN="<your-token>"
BASE="http://127.0.0.1:8000/openapi/v1"

# 1. 查询 meta
echo "=== 查询 meta ==="
curl -s -H "Authorization: Token $TOKEN" "$BASE/skill/meta/" | python -m json.tool

# 2. 发布一篇测试文章
echo "=== 发布文章 ==="
curl -s -X POST "$BASE/skill/articles/publish/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "端到端测试文章",
    "slug": "e2e-test-article",
    "body": "## 端到端测试\n\n这是一篇端到端测试文章，验证完整的发布流程。\n\n### 特性\n\n- 测试 meta 查询\n- 测试 publish 发布",
    "summary": "端到端测试文章，验证完整的发布流程是否正常工作。",
    "category": {"name": "测试分类", "slug": "test-category", "description": "用于测试的分类"},
    "tags": [
      {"name": "端到端", "slug": "e2e", "description": "端到端测试相关"},
      {"name": "测试", "slug": "testing", "description": "软件测试相关"}
    ],
    "keywords": ["测试", "端到端"]
  }' | python -m json.tool
```

预期：
1. meta 查询返回 200，包含 categories/tags/topics
2. publish 返回 201，包含 success: true + id + url + title

---

- [ ] **Step 3: 清理测试数据**

```bash
cd ~/izone && source env/bin/activate
python manage.py shell -c "
from blog.models import Article, Category, Tag, Keyword
Article.objects.filter(slug__in=['e2e-test-article','test-article-001']).delete()
Category.objects.filter(slug__in=['test-category','tech','tech2','tech3']).delete()
Tag.objects.filter(slug__in=['test','e2e','testing']).delete()
Keyword.objects.filter(name__in=['测试','端到端']).delete()
print('Cleaned up')
"
```

---

### Task 9: 项目文档更新

**Files:**
- Modify: `CLAUDE.md`

---

- [ ] **Step 1: 在 CLAUDE.md 中添加 skill 使用说明**

在 `CLAUDE.md` 末尾追加：

```markdown
## Skill: 发布文章 (publish-article)

通过 AI 对话快速发布文章到博客。

**配置**: 编辑 `.claude/skill-publish.json` 设置 API 地址和认证 Token。
Token 在 Django Admin (`/adminx/authtoken/token/`) 中管理。

**使用方式**:
- `发布文章 /path/to/article.md` — 从本地 markdown 文件发布
- `发布文章` 然后粘贴内容 — 从对话中输入

**工作流程**: AI 解析 markdown → 查询已有分类/标签/主题 → 匹配并展示预览 → 用户确认 → 发布（默认存为草稿）

**API 端点**:
- `GET  /openapi/v1/skill/meta/` — 聚合查询分类、标签、主题
- `POST /openapi/v1/skill/articles/publish/` — 发布文章
```

---

- [ ] **Step 2: 提交**

```bash
git add CLAUDE.md
git commit -m "docs: CLAUDE.md 添加 publish-article skill 使用说明

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 完成检查

- [ ] Token 认证全局生效，Admin 中可管理 Token
- [ ] `GET /openapi/v1/skill/meta/` 返回分类、标签、主题
- [ ] `POST /openapi/v1/skill/articles/publish/` 创建文章，校验 + get-or-create + 描述更新
- [ ] 错误响应为中文，格式统一 `{"success": false, "error": "..."}`
- [ ] Skill 指令文件 `.claude/skills/publish-article.md` 可用
- [ ] 配置文件 `.claude/skill-publish.json` 已创建
- [ ] CLAUDE.md 已更新
