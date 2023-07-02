# -*- coding: utf-8 -*-
from django.urls import path
from django.conf import settings
from .views import test_page_view
from .views import (IndexView, DetailView, CategoryView, TagView, AboutView,
                    SilianView, MySearchView, ArchiveView, TimelineView, DetailEditView,
                    update_article, FriendLinkView)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),  # 主页，自然排序
    path('article/<slug:slug>/', DetailView.as_view(), name='detail'),  # 文章内容页
    path('article-edit/<slug:slug>/', DetailEditView.as_view(), name='article_edit'),  # 文章编辑
    path('article-update/', update_article, name='article_update'),  # 文章更新
    path('category/<slug:slug>/', CategoryView.as_view(), name='category'),
    path('tag/<slug:slug>/', TagView.as_view(), name='tag'),
    path('about/', AboutView, name='about'),  # About页面
    path('timeline/', TimelineView.as_view(), name='timeline'),  # timeline页面
    path('archive/', ArchiveView.as_view(), name='archive'),  # 归档页面
    path('silian.xml', SilianView.as_view(content_type='application/xml'), name='silian'),  # 死链页面
    path('search/', MySearchView.as_view(), name='search_view'),  # 全文搜索
    path('friend/', FriendLinkView.as_view(), name='friend'),  # 友情链接
]

if settings.DEBUG:
    urlpatterns.append(path('test/', test_page_view, name='test'))
