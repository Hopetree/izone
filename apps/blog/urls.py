# -*- coding: utf-8 -*-
from django.urls import path
from django.conf import settings
from .views import test_page_view
from .views import (IndexView, DetailView, CategoryView, TagView, AboutView,
                    SilianView, MySearchView, ArchiveView, TimelineView, DetailEditView,
                    update_article, FriendLinkView, friend_add, SubjectDetailView,
                    SubjectPageDetailView, SubjectListView, dashboard, feed_hub)

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
    path('friend/add/', friend_add, name='friend_add'),  # 友情链接申请
    path('dashboard/', dashboard, name='dashboard'),  # 看板
    path('feed-hub/', feed_hub, name='feedhub'),  # feed hub

    # 专题列表页
    path('subject/', SubjectListView.as_view(), name='subject_index'),
    # 专题详情页
    path('subject/<int:pk>/', SubjectPageDetailView.as_view(), name='subject_page'),
    # 专题文章内容页
    path('subject/article/<slug:slug>/', SubjectDetailView.as_view(), name='subject_detail'),

]

if settings.DEBUG:
    urlpatterns.append(path('test/', test_page_view, name='test'))
