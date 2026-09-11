import re
from datetime import datetime
import markdown
from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Q
from django.http import (
    Http404,
    HttpResponseForbidden,
    JsonResponse,
    HttpResponseBadRequest
)
from django.shortcuts import get_object_or_404, render, reverse, redirect
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views import generic
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models.functions import ExtractYear
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension  # 锚点的拓展

from .models import (
    Article,
    Tag,
    Category,
    Timeline,
    Silian,
    AboutBlog,
    FriendLink,
    Subject,
    Fitness,
    Project,
    Note,
)
from .utils import (site_full_url,
                    CustomHtmlFormatter,
                    ApiResponse,
                    ErrorApiResponse,
                    add_views,
                    check_request_headers)
from utils.markdown_ext import (
    DelExtension,
    IconExtension,
    AlertExtension,
    CodeItemExtension,
    CodeGroupExtension
)


def preprocess_mermaid_blocks(md_content):
    """
    处理 Markdown 内容，将 mermaid 代码块转换为 HTML div，并判断是否包含 mermaid 代码块。

    :param md_content: str，原始 Markdown 文本
    :return: (str, bool) -> 处理后的 Markdown 内容 & 是否包含 mermaid 代码块
    """
    # 允许 mermaid 代码块前有 0 个或多个空格 + 可选的换行
    mermaid_pattern = re.compile(r'^\s*```mermaid\s*\n(.*?)\n```', re.DOTALL | re.MULTILINE)

    has_mermaid = False  # 是否包含 mermaid 代码块

    def replace_mermaid_block(match):
        nonlocal has_mermaid
        content = match.group(1).strip()
        if content:  # 仅转换非空 Mermaid 代码块
            has_mermaid = True
            return f"<pre class='mermaid'>\n{content}\n</pre>"
        return match.group(0)  # 保留原始 Markdown

    processed_content = mermaid_pattern.sub(replace_mermaid_block, md_content)

    return processed_content, has_mermaid

def make_markdown():
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown_checklist.extension',
        CodeHiliteExtension(pygments_formatter=CustomHtmlFormatter),
        TocExtension(slugify=slugify),
        DelExtension(),
        IconExtension(),
        AlertExtension(),
        CodeItemExtension(),
        CodeGroupExtension()
    ])
    return md


# Create your views here.

def test_page_view(request):
    return render(request, 'test.html')


def optimize_article_list(queryset):
    """
    文章列表页公共查询优化。

    模板 blog/tags/article_list.html 里每篇文章都会访问 article.category、article.author、
    article.tags、article.get_absolute_url（依赖 topic），并调 get_comment_count 查评论数；
    不提前取好就是每篇 4~5 次额外查询。这里一次性取出关联对象并注解评论数，消除 N+1。
    """
    return queryset.select_related(
        'author', 'category', 'topic'
    ).prefetch_related(
        'tags', 'author__socialaccount_set'
    ).annotate(comment_num=Count('article_comments'))


class ArchiveView(generic.ListView):
    model = Article
    template_name = 'blog/archive.html'
    context_object_name = 'articles'
    paginate_by = 100
    paginate_orphans = 50

    def get_queryset(self, **kwargs):
        # 归档页模板只用标题/日期/链接，链接依赖 topic，预取 topic 即可，不需要标签和评论数
        queryset = super().get_queryset()
        return queryset.filter(is_publish=True).select_related('topic')


class IndexView(generic.ListView):
    model = Article
    template_name = 'blog/index.html'
    context_object_name = 'articles'
    paginate_by = getattr(settings, 'BASE_PAGE_BY', None)
    paginate_orphans = getattr(settings, 'BASE_ORPHANS', 0)

    def get_ordering(self):
        # url参数中可以传排序参数
        sort = self.request.GET.get('sort')
        if sort == 'views':
            return '-views', '-update_date', '-id'
        return '-is_top', '-create_date'

    def get_queryset(self, **kwargs):
        queryset = optimize_article_list(
            super(IndexView, self).get_queryset().filter(is_publish=True)
        )
        sort = self.request.GET.get('sort')
        if sort == 'comment':
            queryset = queryset.order_by('-comment_num', '-views')
        return queryset


class BaseDetailView(generic.DetailView):
    model = Article
    context_object_name = 'article'

    def get_queryset(self):
        # 普通用户只能看发布的文章，作者和管理员可以看到未发布的
        # 预取作者/分类/主题(含所属专题)以及标签/关键词，避免详情页模板逐项回库
        queryset = super().get_queryset().select_related(
            'author', 'category', 'topic__subject'
        ).prefetch_related('tags', 'keywords')
        # 非登录用户可以访问全部发布的文章
        if not self.request.user.is_authenticated:
            return queryset.filter(is_publish=True)
        # 超级管理员访问所有
        if self.request.user.is_superuser:
            return queryset
        # 登录用户访问所有发布和自己的未发布
        return queryset.filter(Q(author=self.request.user) | Q(is_publish=True))

    def get_object(self, queryset=None):
        obj = super().get_object()
        # 设置浏览量增加时间判断,同一篇文章两次浏览超过半小时才重新统计阅览量,作者浏览忽略
        u = self.request.user
        if check_request_headers(self.request.headers):  # 请求头校验通过才计算阅读量
            # 用 Redis SET NX EX 做 30 分钟去重，替代原来读写 DB session 表
            if u != obj.author and not u.is_superuser:
                if cache.add('article:read:{}'.format(obj.id), 1, 60 * 30):
                    obj.update_views()
        # 获取文章更新的时间，判断是否从缓存中取文章的markdown,可以避免每次都转换
        ud = obj.update_date.strftime("%Y%m%d%H%M%S")
        md_key = self.context_object_name + ':markdown:{}:{}'.format(obj.id, ud)
        cache_md = cache.get(md_key)
        if cache_md and settings.DEBUG is False:
            obj.body, obj.toc, obj.has_mermaid = cache_md
        else:
            md = make_markdown()
            processed_content, has_mermaid = preprocess_mermaid_blocks(obj.body)
            obj.body = md.convert(processed_content)
            obj.has_mermaid = has_mermaid
            obj.toc = md.toc
            cache.set(md_key, (obj.body, obj.toc, obj.has_mermaid), 3600 * 24 * 7)
        return obj


class DetailView(BaseDetailView):
    template_name = 'blog/detail.html'

    def get(self, request, *args, **kwargs):
        # 获取实例
        instance = self.get_object()
        # 如果有主题，则跳转到主题格式的文章详情页
        if instance.topic:
            redirect_url = reverse('blog:subject_detail', kwargs={'slug': instance.slug})
            return redirect(redirect_url)
        # 如果不满足条件，则继续处理视图逻辑
        return super().get(request, *args, **kwargs)


class SubjectDetailView(BaseDetailView):
    """
    专题文章视图
    """
    template_name = 'blog/subjectDetail.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(topic__isnull=False)


class CategoryView(generic.ListView):
    model = Article
    template_name = 'blog/category.html'
    context_object_name = 'articles'
    paginate_by = getattr(settings, 'BASE_PAGE_BY', None)
    paginate_orphans = getattr(settings, 'BASE_ORPHANS', 0)

    def get_ordering(self):
        ordering = super(CategoryView, self).get_ordering()
        # url参数中可以传排序参数
        sort = self.request.GET.get('sort')
        if sort == 'views':
            return '-views', '-update_date', '-id'
        return ordering

    def get_category(self):
        # get_queryset 和 get_context_data 都要用到分类对象，缓存一次避免重复查询
        if not hasattr(self, '_category'):
            self._category = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        return self._category

    def get_queryset(self, **kwargs):
        queryset = super(CategoryView, self).get_queryset()
        return optimize_article_list(
            queryset.filter(category=self.get_category(), is_publish=True)
        )

    def get_context_data(self, **kwargs):
        context_data = super(CategoryView, self).get_context_data()
        context_data['search_tag'] = '文章分类'
        context_data['search_instance'] = self.get_category()
        return context_data


class TagView(generic.ListView):
    model = Article
    template_name = 'blog/tag.html'
    context_object_name = 'articles'
    paginate_by = getattr(settings, 'BASE_PAGE_BY', None)
    paginate_orphans = getattr(settings, 'BASE_ORPHANS', 0)

    def get_ordering(self):
        ordering = super(TagView, self).get_ordering()
        # url参数中可以传排序参数
        sort = self.request.GET.get('sort')
        if sort == 'views':
            return '-views', '-update_date', '-id'
        return ordering

    def get_tag(self):
        # get_queryset 和 get_context_data 都要用到标签对象，缓存一次避免重复查询
        if not hasattr(self, '_tag'):
            self._tag = get_object_or_404(Tag, slug=self.kwargs.get('slug'))
        return self._tag

    def get_queryset(self, **kwargs):
        queryset = super(TagView, self).get_queryset()
        return optimize_article_list(
            queryset.filter(tags=self.get_tag(), is_publish=True)
        )

    def get_context_data(self, **kwargs):
        context_data = super(TagView, self).get_context_data()
        context_data['search_tag'] = '文章标签'
        context_data['search_instance'] = self.get_tag()
        return context_data


@add_views('blog:about', 'About页面')
def AboutView(request):
    obj = AboutBlog.objects.first()
    if obj:
        ud = obj.update_date.strftime("%Y%m%d%H%M%S")
        md_key = 'about:markdown:{}:{}'.format(obj.id, ud)
        cache_md = cache.get(md_key)
        if cache_md and settings.DEBUG is False:
            body = cache_md
        else:
            body = obj.body_to_markdown()
            cache.set(md_key, body, 3600 * 24 * 15)
    else:
        repo_url = 'https://github.com/Hopetree'
        body = '<li>作者 Github 地址：<a href="{}">{}</a></li>'.format(repo_url, repo_url)
    return render(request, 'blog/about.html', context={'body': body})


@method_decorator(add_views('blog:timeline', '时间线'), name='get')
class TimelineView(generic.ListView):
    model = Timeline
    template_name = 'blog/timeline.html'
    context_object_name = 'timeline_list'

    def get_ordering(self):
        return '-update_date',


class SilianView(generic.ListView):
    model = Silian
    template_name = 'blog/silian.xml'
    context_object_name = 'badurls'


@method_decorator(add_views('blog:friend', '友链'), name='get')
class FriendLinkView(generic.ListView):
    model = FriendLink
    template_name = 'blog/friend.html'
    context_object_name = 'friend_list'

    def get_queryset(self):
        queryset = super(FriendLinkView, self).get_queryset()
        return queryset.filter(is_show=True, is_active=True)


# 重写搜索视图，可以增加一些额外的参数，且可以重新定义名称
# 使用 MySQL FULLTEXT(n-gram) 实现站内搜索，替换原 haystack + whoosh 方案
class MySearchView(generic.ListView):
    template_name = 'search/blog/search.html'
    context_object_name = 'search_list'
    paginate_by = getattr(settings, 'BASE_PAGE_BY', None)
    paginate_orphans = getattr(settings, 'BASE_ORPHANS', 0)

    def get_queryset(self):
        self.query = self.request.GET.get('q', '').strip()
        queryset = Article.objects.filter(is_publish=True)
        if self.query:
            # 移除 BOOLEAN MODE 的语法操作符，避免用户输入特殊字符干扰查询语义
            term = re.sub(r'[+\-<>\\(\\)~*"@\\]', ' ', self.query)
            term = re.sub(r'\s+', ' ', term).strip()
            if term:
                queryset = queryset.extra(
                    where=["MATCH(title, body, summary) AGAINST (%s IN BOOLEAN MODE)"],
                    params=[term],
                )
                # n-gram 分词对英文会产生宽泛命中(如 django 命中含 ng/go 的文章)，用子串过滤收紧
                for word in term.split():
                    queryset = queryset.filter(
                        Q(title__icontains=word) | Q(body__icontains=word) | Q(summary__icontains=word)
                    )
            else:
                queryset = queryset.none()
        return queryset.order_by('-views')

    def get_context_data(self, **kwargs):
        context = super(MySearchView, self).get_context_data(**kwargs)
        context['query'] = self.query
        return context


def robots(request):
    site_url = site_full_url()
    return render(request, 'robots.txt', context={'site_url': site_url}, content_type='text/plain')


class DetailEditView(generic.DetailView):
    """
    文章编辑视图
    """
    model = Article
    template_name = 'blog/articleEdit.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        obj = super(DetailEditView, self).get_object()
        # 非作者及超管无权访问
        if not self.request.user.is_superuser and obj.author != self.request.user:
            raise Http404('Invalid request.')
        return obj


@require_http_methods(["POST"])
def update_article(request):
    """更新文章，仅管理员和作者可以更新"""
    if request.method == 'POST' and request.is_ajax():
        article_slug = request.POST.get('article_slug')
        article_body = request.POST.get('article_body')
        article_img_link = request.POST.get('article_img_link')
        change_img_link_flag = request.POST.get('change_img_link_flag')

        try:
            article = Article.objects.get(slug=article_slug)
            # 检查当前用户是否是作者
            if not request.user.is_superuser and article.author != request.user:
                return HttpResponseForbidden("You don't have permission to update this article.")

            # 更新article模型的数据
            article.body = article_body
            if change_img_link_flag == 'true':
                article.img_link = article_img_link  # 更新封面图地址
            article.save()  # 这里不要设置更新的字段，不然会导致其他要在save更新的字段不更新

            callback = article.get_absolute_url()
            response_data = {'message': 'Success', 'data': {'callback': callback}, 'code': 0}
            return JsonResponse(response_data)
        except Article.DoesNotExist:
            return HttpResponseBadRequest("Article not found.")
    return HttpResponseBadRequest("Invalid request.")


@require_http_methods(["POST"])
def delete_article(request):
    """删除文章，仅管理员和作者可以操作"""
    if not request.is_ajax():
        return HttpResponseBadRequest("Invalid request.")
    article_slug = request.POST.get('article_slug')
    try:
        article = Article.objects.get(slug=article_slug)
        if not request.user.is_superuser and article.author != request.user:
            return JsonResponse({'message': '无权限操作', 'code': 1}, status=403)
        article.delete()
        return JsonResponse({'message': '删除成功', 'code': 0})
    except Article.DoesNotExist:
        return JsonResponse({'message': '文章不存在', 'code': 1}, status=404)


@require_http_methods(["POST"])
def publish_article(request):
    """发布文章（将草稿转为已发布），仅管理员和作者可以操作"""
    article_slug = request.POST.get('article_slug')
    try:
        article = Article.objects.get(slug=article_slug)
        if not request.user.is_superuser and article.author != request.user:
            return JsonResponse({'message': '无权限操作', 'code': 1}, status=403)
        if article.is_publish:
            return JsonResponse({'message': '文章已是发布状态', 'code': 1})
        article.is_publish = True
        article.save()  # save() 会自动更新 create_date 为发布时间
        return JsonResponse({
            'message': '发布成功',
            'code': 0,
            'data': {'url': article.get_absolute_url()}
        })
    except Article.DoesNotExist:
        return JsonResponse({'message': '文章不存在', 'code': 1}, status=404)


def friend_add(request):
    """
    申请友链
    @param request:
    @return:
    """
    if request.method == "POST" and request.is_ajax():
        data = request.POST
        name = data.get('name')
        description = data.get('description')
        link = data.get('link')

        try:
            friend = FriendLink.objects.create(name=name,
                                               description=description,
                                               link=link,
                                               is_active=False,
                                               is_show=True,
                                               )
            resp = ApiResponse()
            resp.data = {'id': friend.id}
            return resp.as_json_response()
        except Exception as e:
            resp = ErrorApiResponse()
            resp.error = str(e)
            return resp.as_json_response()

    return render(request, 'blog/friendAdd.html')


# 专题详情页
class SubjectPageDetailView(generic.DetailView):
    model = Subject
    template_name = 'blog/subject.html'
    context_object_name = 'subject'


# 专题列表页
class SubjectListView(generic.ListView):
    model = Subject
    template_name = 'blog/subjectIndex.html'
    context_object_name = 'subjects'
    paginate_by = 100
    paginate_orphans = 0

    def get_queryset(self):
        # 注解专题下已发布文章数，替代模板里逐个专题调 subject.get_article_count
        return super().get_queryset().annotate(
            article_count=Count('topics__articles',
                                filter=Q(topics__articles__is_publish=True))
        )


class TagListView(generic.ListView):
    model = Tag
    template_name = 'blog/tagIndex.html'
    context_object_name = 'tags'
    paginate_by = 100
    paginate_orphans = 0

    def get_ordering(self):
        return 'name',

    def get_queryset(self):
        # 注解每个标签下已发布文章数，模板直接取 total_num；原模板用 tag.get_article_list.count 是每个标签一次 COUNT
        queryset = super().get_queryset()
        return queryset.annotate(
            total_num=Count('article', filter=Q(article__is_publish=True))
        )


# dashboard页面，仅管理员可以访问，其他用户不能访问
def dashboard(request):
    if request.user.is_staff:
        return render(request, 'blog/dashboard.html')
    return render(request, '403.html')


# feed hub
def feed_hub(request):
    return render(request, 'blog/feedhub.html')


@csrf_exempt
def vitepress_subject_view(request):
    data = {'code': 0, 'error': '', 'data': []}
    subjects = Subject.objects.all()
    for subject in subjects:
        subject_data = {
            'name': subject.name,
            'description': subject.description,
            'pk': str(subject.pk),
            'items': []
        }
        for topic in subject.get_topics():
            topic_data = {
                'name': topic.name,
                'items': []
            }
            for article in topic.get_articles():
                topic_data['items'].append({
                    'title': article.title,
                    'slug': article.slug
                })
            subject_data['items'].append(topic_data)
        data['data'].append(subject_data)
    return JsonResponse(data)


def get_year_list():
    this_year = datetime.today().year
    # 从Fitness模型中提取年份
    years = (
        Fitness.objects
        .annotate(year=ExtractYear('run_date'))  # 从run_date中提取年份
        .values_list('year', flat=True)  # 仅获取年份字段
        .distinct()  # 去重
    )
    years = sorted(list(set(years)))
    if this_year not in years:
        years.append(this_year)
    # 转换为列表并排序
    return sorted(list(set(years)))


@add_views('blog:health', '慢跑看板')
def health(request):
    current_year = request.GET.get('year', datetime.today().year)
    year_list = get_year_list()
    context = {'current_year': int(current_year), 'year_list': year_list}
    return render(request, 'blog/health.html', context)


class ProjectListView(generic.ListView):
    model = Project
    template_name = 'blog/projectIndex.html'
    context_object_name = 'projects'
    paginate_by = 100
    paginate_orphans = 0


@method_decorator(add_views('blog:note_index', '便签笔记'), name='get')
class NoteIndexView(TemplateView):
    template_name = 'blog/noteIndex.html'

# standalone api view
@csrf_exempt
def notes_api(request):
    """GET: Return published notes as JSON list. POST: Create/update note (admin only)."""
    if request.method == 'POST':
        if not request.user.is_staff:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        try:
            import json
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        note_id = data.get('id')
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        tags = data.get('tags', '').strip()
        is_publish = data.get('is_publish', True)

        if not title:
            return JsonResponse({'error': '标题不能为空'}, status=400)

        if note_id:
            try:
                note = Note.objects.get(pk=note_id)
            except Note.DoesNotExist:
                return JsonResponse({'error': '笔记不存在'}, status=404)
            note.title = title
            note.content = content
            note.tags = tags
            note.is_publish = is_publish
            note.save()
        else:
            note = Note.objects.create(
                title=title, content=content, tags=tags, is_publish=is_publish
            )

        return JsonResponse({
            'id': note.pk,
            'title': note.title,
            'content': note.content,
            'tags': note.get_tag_list(),
            'is_publish': note.is_publish,
        }, json_dumps_params={'ensure_ascii': False})

    # GET
    notes_qs = Note.objects.filter(is_publish=True).order_by('-create_date')
    notes_list = [
        {
            'id': n.pk,
            'title': n.title,
            'content': n.content,
            'tags': n.get_tag_list(),
        }
        for n in notes_qs
    ]
    return JsonResponse(notes_list, safe=False, json_dumps_params={'ensure_ascii': False})