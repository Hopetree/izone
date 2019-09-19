# -*- coding: utf-8 -*-
from django.urls import path
# from .views import goview
from .views import (IndexView, DetailView, CategoryView, TagView, AboutView,
                    SilianView, MySearchView, ArchiveView, TimelineView)

urlpatterns = [
    # path('go/', goview, name='go'),  # 测试用页面

    path('', IndexView.as_view(), name='index'),  # 主页，自然排序
    path('hot/', IndexView.as_view(), {'sort': 'v'}, name='index_hot'),  # 主页，按照浏览量排序
    path('article/<slug:slug>/', DetailView.as_view(), name='detail'),  # 文章内容页
    path('category/<slug:slug>/', CategoryView.as_view(), name='category'),
    path('category/<slug:slug>/hot/', CategoryView.as_view(), {'sort': 'v'},
        name='category_hot'),
    path('tag/<slug:slug>/', TagView.as_view(), name='tag'),
    path('tag/<slug:slug>/hot/', TagView.as_view(), {'sort': 'v'}, name='tag_hot'),
    path('about/', AboutView, name='about'),  # About页面
    path('timeline/', TimelineView.as_view(), name='timeline'),  # timeline页面
    path('archive/', ArchiveView.as_view(), name='archive'),  # 归档页面
    path('silian.xml', SilianView.as_view(content_type='application/xml'), name='silian'),  # 死链页面
    path('search/', MySearchView.as_view(), name='search_view'),  # 全文搜索
]
