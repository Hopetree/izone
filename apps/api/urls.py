# -*- coding:utf-8 -*-
# @Date  : 2019/2/1

from rest_framework.routers import DefaultRouter
from .views import (UserListSet, ArticleListSet, TagListSet,
                    CategoryListSet, TimelineListSet, ToolLinkListSet)

router = DefaultRouter()
router.register(r'users', UserListSet)
router.register(r'articles', ArticleListSet)
router.register(r'tags', TagListSet)
router.register(r'categorys', CategoryListSet)
router.register(r'timelines', TimelineListSet)
router.register(r'toollinks', ToolLinkListSet)
