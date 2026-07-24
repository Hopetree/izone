# -*- coding:utf-8 -*-
# @Date  : 2019/2/1

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (UserListSet, ArticleListSet, TagListSet,
                    CategoryListSet, TimelineListSet,
                    ToolLinkListSet, NavigationSiteListSet,
                    SkillMetaView, SkillPublishView,
                    SkillArticleQueryView, SkillImageUploadView,
                    SkillArticleCoverView)
from scripts.views import SkillScriptCreateUpdateView

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
    path('skill/images/upload/', SkillImageUploadView.as_view(), name='skill-image-upload'),
    path('skill/articles/', SkillArticleQueryView.as_view(), name='skill-article-query'),
    path('skill/articles/publish/', SkillPublishView.as_view(), name='skill-publish'),
    path('skill/articles/cover/', SkillArticleCoverView.as_view(), name='skill-article-cover'),
    path('skill/scripts/save/', SkillScriptCreateUpdateView.as_view(), name='skill-script-save'),
]
