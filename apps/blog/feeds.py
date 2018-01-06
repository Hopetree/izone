# -*- coding: utf-8 -*-
from django.contrib.syndication.views import Feed
from .models import Article
from django.conf import settings

class AllArticleRssFeed(Feed):
    # 显示在聚会阅读器上的标题
    title = settings.SITE_END_TITLE
    # 跳转网址，为主页
    link = "/"
    # 描述内容
    description = settings.SITE_DESCRIPTION
    # 需要显示的内容条目，这个可以自己挑选一些热门或者最新的博客
    def items(self):
        return Article.objects.all()[:100]

    # 显示的内容的标题,这个才是最主要的东西
    def item_title(self, item):
        return "【{}】{}".format(item.category,item.title)

    # 显示的内容的描述
    def item_description(self, item):
        return item.body_to_markdown()