# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import goview
from .views import (IndexView, DetailView, CategoryView, TagView, AboutView,
                    SilianView, MySearchView, ArchiveView, TimelineView)
from django.views.decorators.cache import cache_page

urlpatterns = [
    # url(r'^go/$', goview, name='go'),  # 测试用页面

    url(r'^$', cache_page(60 * 30)(IndexView.as_view()), name='index'),  # 主页，自然排序
    url(r'^hot/$', cache_page(60 * 30)(IndexView.as_view()), {'sort': 'v'}, name='index_hot'),  # 主页，按照浏览量排序
    url(r'^article/(?P<slug>[\w-]+)/$', DetailView.as_view(), name='detail'),  # 文章内容页
    url(r'^category/(?P<slug>[\w-]+)/$', cache_page(60 * 60 * 2)(CategoryView.as_view()), name='category'),
    url(r'^category/(?P<slug>[\w-]+)/hot/$', cache_page(60 * 60 * 4)(CategoryView.as_view()), {'sort': 'v'},
        name='category_hot'),
    url(r'^tag/(?P<slug>[\w-]+)/$', cache_page(60 * 60 * 2)(TagView.as_view()), name='tag'),
    url(r'^tag/(?P<slug>[\w-]+)/hot/$', cache_page(60 * 60 * 4)(TagView.as_view()), {'sort': 'v'}, name='tag_hot'),
    url(r'^about/$', cache_page(60 * 60 * 24)(AboutView), name='about'),  # About页面
    url(r'^timeline/$', cache_page(60 * 60 * 24)(TimelineView.as_view()), name='timeline'),  # timeline页面
    url(r'archive/$', cache_page(60 * 60 * 5)(ArchiveView.as_view()), name='archive'),  # 归档页面
    url(r'^silian\.xml$', SilianView.as_view(content_type='application/xml'), name='silian'),  # 死链页面
    url(r'^search/$', MySearchView.as_view(), name='search_view'),  # 全文搜索
]
