from .models import Article, Tag, Category, Timeline, Silian
from django.shortcuts import get_object_or_404, render
from django.utils.text import slugify
from django.views import generic
from django.conf import settings
from markdown.extensions.toc import TocExtension  # 锚点的拓展
import markdown
import time


# Create your views here.

class IndexView(generic.ListView):
    model = Article
    template_name = 'blog/index.html'
    context_object_name = 'articles'
    paginate_by = settings.BASE_PAGE_BY
    paginate_orphans = settings.BASE_ORPHANS

    def get_ordering(self):
        ordering = super(IndexView, self).get_ordering()
        sort = self.kwargs.get('sort')
        if sort == 'v':
            return ('-views','-update_date','-id')
        return ordering

class DetailView(generic.DetailView):
    model = Article
    template_name = 'blog/detail.html'
    context_object_name = 'article'

    def get_object(self):
        obj = super(DetailView, self).get_object()
        # 设置浏览量增加时间判断,同一篇文章两次浏览超过2小时才重新统计阅览量,作者浏览忽略
        u = self.request.user
        ses = self.request.session
        the_key = 'is_read_{}'.format(obj.id)
        is_read_time = ses.get(the_key)
        if u != obj.author:
            if not is_read_time:
                obj.update_views()
                ses[the_key] = time.time()
            else:
                now_time = time.time()
                t = now_time - is_read_time
                if t > 7200:
                    obj.update_views()
                    ses[the_key] = time.time()
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            TocExtension(slugify=slugify),
        ])
        obj.body = md.convert(obj.body)
        obj.toc = md.toc
        return obj

class CategoryView(generic.ListView):
    model = Article
    template_name = 'blog/category.html'
    context_object_name = 'articles'
    paginate_by = settings.BASE_PAGE_BY
    paginate_orphans = settings.BASE_ORPHANS

    def get_ordering(self):
        ordering = super(CategoryView, self).get_ordering()
        sort = self.kwargs.get('sort')
        if sort == 'v':
            return ('-views','-update_date','-id')
        return ordering

    def get_queryset(self, **kwargs):
        queryset = super(CategoryView, self).get_queryset()
        cate = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        return queryset.filter(category=cate)

    def get_context_data(self, **kwargs):
        context_data = super(CategoryView, self).get_context_data()
        cate = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        context_data['search_tag'] = '文章分类'
        context_data['search_instance'] = cate
        return context_data

class TagView(generic.ListView):
    model = Article
    template_name = 'blog/tag.html'
    context_object_name = 'articles'
    paginate_by = settings.BASE_PAGE_BY
    paginate_orphans = settings.BASE_ORPHANS

    def get_ordering(self):
        ordering = super(TagView, self).get_ordering()
        sort = self.kwargs.get('sort')
        if sort == 'v':
            return ('-views','-update_date','-id')
        return ordering

    def get_queryset(self, **kwargs):
        queryset = super(TagView, self).get_queryset()
        tag = get_object_or_404(Tag, slug=self.kwargs.get('slug'))
        return queryset.filter(tags=tag)

    def get_context_data(self, **kwargs):
        context_data = super(TagView, self).get_context_data()
        tag = get_object_or_404(Tag, slug=self.kwargs.get('slug'))
        context_data['search_tag'] = '文章标签'
        context_data['search_instance'] = tag
        return context_data



