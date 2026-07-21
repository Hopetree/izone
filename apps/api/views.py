# -*- coding: utf-8 -*-

from django.conf import settings
from rest_framework import viewsets, permissions
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from webstack.models import NavigationSite

from blog.models import Article, Tag, Category, Timeline
from oauth.models import Ouser
from tool.models import ToolLink
from .serializers import (UserSerializer, ArticleSerializer,
                          TimelineSerializer, TagSerializer,
                          CategorySerializer, ToolLinkSerializer,
                          NavigationSiteSerializer)


# from .permissions import IsAdminUserOrReadOnly

# RESEful API VIEWS
class UserListSet(viewsets.ModelViewSet):
    queryset = Ouser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class ArticleListSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    # 使用全局认证方案（TokenAuthentication + SessionAuthentication + BasicAuthentication）
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        # 仅返回 is_publish=True 的数据
        return Article.objects.filter(is_publish=True)


class TagListSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class CategoryListSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class TimelineListSet(viewsets.ModelViewSet):
    queryset = Timeline.objects.all()
    serializer_class = TimelineSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class ToolLinkListSet(viewsets.ModelViewSet):
    queryset = ToolLink.objects.all()
    serializer_class = ToolLinkSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class NavigationSiteListSet(viewsets.ModelViewSet):
    queryset = NavigationSite.objects.all()
    serializer_class = NavigationSiteSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        is_show = self.request.query_params.get('is_show', None)
        if is_show == 'true':
            queryset = queryset.filter(is_show=True)
        elif is_show == 'false':
            queryset = queryset.filter(is_show=False)
        return queryset


# ==================== Skill 专用 Views ====================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers as drf_serializers
from blog.models import Topic
from .serializers import SkillCategorySerializer, SkillTagSerializer, SkillTopicSerializer


class SkillMetaView(APIView):
    """聚合返回分类、标签、主题、专题列表，供 skill 匹配决策"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from blog.models import Subject
        categories = Category.objects.all()
        tags = Tag.objects.all()
        topics = Topic.objects.select_related('subject').all()
        subjects = Subject.objects.all()

        return Response({
            'categories': SkillCategorySerializer(categories, many=True).data,
            'tags': SkillTagSerializer(tags, many=True).data,
            'topics': SkillTopicSerializer(topics, many=True).data,
            'subjects': [
                {'id': s.id, 'name': s.name, 'status': s.status}
                for s in subjects
            ],
        })


from .serializers import ArticlePublishSerializer


class SkillImageUploadView(APIView):
    """Skill 专用封面上传接口，接受 PNG/JPG/SVG"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'success': False, 'error': '请上传图片文件'}, status=400)

        ext = file.name.split('.')[-1].lower() if '.' in file.name else ''
        if ext not in ('png', 'jpg', 'jpeg', 'svg'):
            return Response({'success': False, 'error': f'不支持的文件类型: .{ext}'}, status=400)

        import uuid, os
        from datetime import datetime

        name = f"{uuid.uuid4().hex}.png"
        today = datetime.now()
        relative_path = f"article/upload/{today.strftime('%Y/%m/%d')}"
        upload_dir = os.path.join(settings.MEDIA_ROOT, relative_path)
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, name)

        if ext == 'svg':
            import platform, subprocess, tempfile
            svg_data = file.read()
            if platform.system() == 'Darwin':
                # macOS: qlmanage + PIL 裁剪
                with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
                    tmp.write(svg_data)
                    tmp_path = tmp.name
                try:
                    subprocess.run(['qlmanage', '-t', '-s', '500', '-o', upload_dir, tmp_path],
                                   capture_output=True, timeout=10)
                    generated = os.path.join(upload_dir, os.path.basename(tmp_path) + '.png')
                    if os.path.exists(generated):
                        from PIL import Image
                        img = Image.open(generated)
                        # qlmanage 输出 500×500，内容在顶部，从顶部裁剪 500×300
                        img = img.crop((0, 0, 500, 300))
                        img.save(filepath, 'PNG')
                        os.unlink(generated)
                finally:
                    os.unlink(tmp_path)
            else:
                # Linux/Docker: cairosvg
                try:
                    import cairosvg
                    cairosvg.svg2png(bytestring=svg_data, write_to=filepath,
                                     output_width=500, output_height=300)
                except ImportError:
                    return Response({
                        'success': False,
                        'error': '服务器缺少 cairosvg，请检查 requirements.txt'
                    }, status=500)
            if not os.path.exists(filepath):
                return Response({'success': False, 'error': 'SVG 转换失败'}, status=500)
        else:
            from PIL import Image
            img = Image.open(file)
            img = img.convert('RGBA')
            img.thumbnail((500, 300), Image.LANCZOS)
            bg = Image.new('RGBA', (500, 300), (255, 255, 255, 255))
            bg.paste(img, ((500 - img.width) // 2, (300 - img.height) // 2),
                     img if img.mode == 'RGBA' else None)
            bg = bg.convert('RGB')
            bg.save(filepath, 'PNG')

        img_path = f"{relative_path}/{name}"
        return Response({'success': True, 'url': img_path}, status=201)


class SkillArticleCoverView(APIView):
    """单独更新文章封面图"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        slug = request.data.get('slug', '').strip()
        img_link = request.data.get('img_link', '').strip()
        if not slug:
            return Response({'success': False, 'error': '请提供 slug'}, status=400)
        if not img_link:
            return Response({'success': False, 'error': '请提供 img_link'}, status=400)
        if img_link.startswith('/media/'):
            img_link = img_link[7:]

        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response({'success': False, 'error': '文章不存在'}, status=404)

        article.img_link = img_link
        article.save(update_fields=['img_link'])
        return Response({'success': True, 'url': img_link})


class SkillArticleQueryView(APIView):
    """按 slug 查询文章，供 skill 判断是创建还是更新"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        slug = request.query_params.get('slug', '').strip()
        if not slug:
            return Response({'success': False, 'error': '请提供 slug 参数'}, status=400)

        try:
            article = Article.objects.get(slug=slug)
            topic = article.topic
            return Response({
                'success': True,
                'exists': True,
                'article': {
                    'id': article.id,
                    'title': article.title,
                    'slug': article.slug,
                    'body': article.body,
                    'summary': article.summary,
                    'is_publish': article.is_publish,
                    'is_top': article.is_top,
                    'img_link': str(article.img_link) if article.img_link else '',
                    'category': {
                        'name': article.category.name,
                        'slug': article.category.slug,
                        'description': article.category.description,
                    } if article.category else None,
                    'tags': [{
                        'name': t.name,
                        'slug': t.slug,
                        'description': t.description,
                    } for t in article.tags.all()],
                    'keywords': [k.name for k in article.keywords.all()],
                    'topic': {
                        'id': topic.id,
                        'name': topic.name,
                        'subject_id': topic.subject.id,
                        'subject_name': topic.subject.name,
                    } if topic else None,
                    'topic_order': article.topic_order,
                    'topic_short_title': article.topic_short_title,
                    'create_date': article.create_date.strftime('%Y-%m-%d %H:%M'),
                    'update_date': article.update_date.strftime('%Y-%m-%d %H:%M'),
                }
            })
        except Article.DoesNotExist:
            return Response({'success': True, 'exists': False})


class SkillPublishView(APIView):
    """Skill 专用文章发布/更新接口，slug 已存在则更新，否则创建"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        slug = request.data.get('slug', '')
        article = Article.objects.filter(slug=slug).first() if slug else None
        is_update = article is not None

        serializer = ArticlePublishSerializer(
            article, data=request.data, context={'request': request}
        ) if is_update else ArticlePublishSerializer(
            data=request.data, context={'request': request}
        )

        if not serializer.is_valid():
            errors = serializer.errors
            first_field = next(iter(errors))
            first_error = errors[first_field]
            if isinstance(first_error, list):
                msg = first_error[0]
            elif isinstance(first_error, dict):
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
                'action': 'update' if is_update else 'create',
            }, status=200 if is_update else 201)
        except drf_serializers.ValidationError as e:
            detail = e.detail
            msg = detail[0] if isinstance(detail, list) else str(detail)
            return Response({'success': False, 'error': msg}, status=400)
