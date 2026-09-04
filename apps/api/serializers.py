# -*- coding: utf-8 -*-
from oauth.models import Ouser
from rest_framework import serializers
from blog.models import Article, Tag, Category, Timeline, Topic, Keyword
from tool.models import ToolLink, ToolCategory
from webstack.models import NavigationSite


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ouser
        fields = ('id', 'username', 'first_name', 'link', 'avatar')
        # fields = '__all__'
        # exclude = ('password','email')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    subject = serializers.ReadOnlyField(source='topic.subject.pk')
    category = CategorySerializer(
        many=False,
        read_only=True,
    )
    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    keywords = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = Article
        # fields = ('id', 'author', 'title', 'views', 'category', 'tags')
        fields = '__all__'
        # exclude = ('body',)


class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = '__all__'


class ToolCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolCategory
        fields = '__all__'


class ToolLinkSerializer(serializers.ModelSerializer):
    category = ToolCategorySerializer()

    class Meta:
        model = ToolLink
        fields = '__all__'


class NavigationSiteSerializer(serializers.ModelSerializer):
    menu = serializers.ReadOnlyField(source='menu.name')
    class Meta:
        model = NavigationSite
        fields = '__all__'


# ==================== Skill 专用 Serializers ====================

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


# ==================== Skill Publish Serializer ====================

class CategoryField(serializers.DictField):
    """分类字段：接收 {name, slug, description}"""
    child = serializers.CharField()


class TagItemField(serializers.DictField):
    """标签字段：接收 {name, slug, description}"""
    child = serializers.CharField()


class TopicField(serializers.DictField):
    """主题字段：接收 {id?, name?, subject_id?}"""
    child = serializers.CharField(required=False)


class ArticlePublishSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=150, required=True, allow_blank=False)
    slug = serializers.SlugField(max_length=50, required=True, allow_blank=False)
    body = serializers.CharField(required=True, allow_blank=False, trim_whitespace=False)
    summary = serializers.CharField(max_length=230, required=True, allow_blank=False)
    is_publish = serializers.BooleanField(default=False)
    is_top = serializers.BooleanField(default=False)
    category = CategoryField(required=True)
    tags = serializers.ListField(child=TagItemField(), required=False, default=list)
    keywords = serializers.ListField(
        child=serializers.CharField(max_length=20), required=False, default=list
    )
    img_link = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_img_link(self, value):
        if value and value.startswith('/media/'):
            value = value[7:]  # strip /media/ prefix
        return value
    topic = TopicField(required=False, allow_null=True, default=None)
    topic_order = serializers.IntegerField(required=False, default=99)
    topic_short_title = serializers.CharField(
        max_length=50, required=False, allow_blank=True, default=''
    )

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("标题不能为空")
        if len(value) > 150:
            raise serializers.ValidationError(
                f"标题长度不能超过 150 字符，当前 {len(value)} 字符"
            )
        return value.strip()

    def validate_slug(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("slug 不能为空")
        return value.strip()

    def validate_body(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("文章正文不能为空")
        return value

    def validate_summary(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("文章摘要不能为空")
        value = value.strip()
        if len(value) > 230:
            raise serializers.ValidationError(
                f"摘要长度不能超过 230 字符，当前 {len(value)} 字符"
            )
        return value

    def validate_category(self, value):
        name = value.get('name', '').strip()
        slug = value.get('slug', '').strip()
        if not name:
            raise serializers.ValidationError("category.name 为必填项")
        if len(name) > 20:
            raise serializers.ValidationError(
                f"分类名长度不能超过 20 字符，当前 {len(name)} 字符"
            )
        if not slug:
            raise serializers.ValidationError("category.slug 为必填项")
        if len(slug) > 50:
            raise serializers.ValidationError("分类 slug 长度不能超过 50 字符")
        if Category.objects.filter(slug=slug).exists():
            existing = Category.objects.filter(name=name).first()
            if not existing or existing.slug != slug:
                raise serializers.ValidationError(
                    f"分类 slug '{slug}' 已被占用"
                )
        return {
            'name': name,
            'slug': slug,
            'description': value.get('description', '分类描述').strip(),
        }

    def validate_tags(self, value):
        cleaned = []
        for tag in value:
            name = tag.get('name', '').strip()
            slug = tag.get('slug', '').strip()
            if not name:
                raise serializers.ValidationError("tag.name 为必填项")
            if len(name) > 20:
                raise serializers.ValidationError(
                    f"标签名 '{name}' 长度不能超过 20 字符，当前 {len(name)} 字符"
                )
            if not slug:
                raise serializers.ValidationError("tag.slug 为必填项")
            if len(slug) > 50:
                raise serializers.ValidationError(
                    f"标签 '{name}' slug 长度不能超过 50 字符"
                )
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
        subject_id = value.get('subject_id')

        # 按 ID 查已有主题
        if topic_id:
            try:
                return Topic.objects.get(pk=int(topic_id))
            except (Topic.DoesNotExist, ValueError):
                pass

        # 按名称查已有主题
        if topic_name:
            topic = Topic.objects.filter(name=topic_name).first()
            if topic:
                return topic

        # 不存在，尝试新建（必须有 subject_id）
        if topic_name and subject_id:
            from blog.models import Subject
            try:
                subject = Subject.objects.get(pk=int(subject_id))
            except (Subject.DoesNotExist, ValueError):
                available = Subject.objects.values_list('name', flat=True)[:20]
                raise serializers.ValidationError(
                    f"专题 id={subject_id} 不存在，可用专题: {', '.join(available)}"
                )
            # 不需要 slug，Topic 模型没有 slug 字段
            topic = Topic.objects.create(
                name=topic_name,
                subject=subject,
            )
            return topic

        # 无法创建，列出可用的
        available = Topic.objects.select_related('subject')[:30]
        available_list = ', '.join(
            f'[{t.subject.name}]{t.name}' for t in available
        ) if available else '(无)'
        raise serializers.ValidationError(
            f"主题 '{topic_name or topic_id}' 不存在。要新建主题请提供 subject_id。"
            f"可用主题: {available_list}"
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
                    f"分类 '{category_name}' 不存在，尝试创建时 slug '{slug}' "
                    f"已被分类 '{conflict.name}' 占用"
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
                        f"标签 '{tag_name}' 不存在，尝试创建时 slug '{slug}' "
                        f"已被标签 '{conflict.name}' 占用"
                    )
                tag = Tag.objects.create(
                    name=tag_name,
                    slug=slug,
                    description=tag_data.get('description', '标签描述'),
                )
            tag_objects.append(tag)

        # 处理 keywords: get-or-create
        # 注意：MySQL utf8mb4 默认排序规则大小写不敏感，同名(含大小写差异)记录可能不止一条，
        # get_or_create 的 get() 会抛 MultipleObjectsReturned，所以这里先 filter 取第一条
        keyword_objects = []
        for kw_name in keywords_data:
            kw = Keyword.objects.filter(name=kw_name.strip()).first()
            if kw is None:
                kw = Keyword.objects.create(name=kw_name.strip())
            keyword_objects.append(kw)

        # 创建文章
        article_kwargs = dict(
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
        img_link = validated_data.get('img_link', '')
        if img_link:
            article_kwargs['img_link'] = img_link
        article = Article.objects.create(**article_kwargs)
        article.tags.set(tag_objects)
        article.keywords.set(keyword_objects)

        return article

    def update(self, instance, validated_data):
        request = self.context['request']
        category_data = validated_data.pop('category')
        tags_data = validated_data.pop('tags', [])
        keywords_data = validated_data.pop('keywords', [])
        topic = validated_data.pop('topic', None)

        # 处理 category
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
                    f"分类 '{category_name}' 不存在，尝试创建时 slug '{slug}' "
                    f"已被分类 '{conflict.name}' 占用"
                )
            category = Category.objects.create(
                name=category_name,
                slug=slug,
                description=category_data.get('description', '分类描述'),
            )

        # 处理 tags
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
                        f"标签 '{tag_name}' 不存在，尝试创建时 slug '{slug}' "
                        f"已被标签 '{conflict.name}' 占用"
                    )
                tag = Tag.objects.create(
                    name=tag_name,
                    slug=slug,
                    description=tag_data.get('description', '标签描述'),
                )
            tag_objects.append(tag)

        # 处理 keywords
        keyword_objects = []
        for kw_name in keywords_data:
            kw, _ = Keyword.objects.get_or_create(name=kw_name.strip())
            keyword_objects.append(kw)

        # 更新文章字段
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.summary = validated_data.get('summary', instance.summary)
        img_link = validated_data.get('img_link', '')
        if img_link:
            instance.img_link = img_link
        instance.is_publish = validated_data.get('is_publish', instance.is_publish)
        instance.is_top = validated_data.get('is_top', instance.is_top)
        instance.category = category
        instance.topic = topic
        instance.topic_order = validated_data.get('topic_order', instance.topic_order)
        instance.topic_short_title = validated_data.get('topic_short_title', '') or ''
        instance.save()
        instance.tags.set(tag_objects)
        instance.keywords.set(keyword_objects)

        return instance
