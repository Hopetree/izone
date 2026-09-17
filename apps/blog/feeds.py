# -*- coding: utf-8 -*-
from xml.sax.saxutils import escape
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from .models import Article
from django.conf import settings

# feed 正文缓存时间（秒）；key 里带 update_date，文章改动会自动失效
FEED_BODY_CACHE_SECONDS = 3600 * 24 * 7


class AllArticleRssFeed(Feed):
    # 显示在聚会阅读器上的标题
    title = settings.SITE_END_TITLE
    # 跳转网址，为主页
    link = "/"
    # 描述内容
    description = settings.SITE_DESCRIPTION

    # 需要显示的内容条目，这个可以自己挑选一些热门或者最新的博客
    def items(self):
        return Article.objects.filter(is_publish=True)[:10]

    # 显示的内容的标题,这个才是最主要的东西
    def item_title(self, item):
        return item.title

    # 显示的内容的描述
    def item_description(self, item):
        # 阅读器会反复抓取 feed，正文渲染（markdown + Pygments）很贵，这里单独缓存一份；
        # 不复用文章详情页的 article:markdown:* 缓存，因为那边的元组结构不同、会被互相覆盖
        cache_key = 'feed:article:body:{}:{}'.format(
            item.id, item.update_date.strftime('%Y%m%d%H%M%S'))
        body = cache.get(cache_key)
        if body is None:
            body = item.body_to_markdown()
            cache.set(cache_key, body, FEED_BODY_CACHE_SECONDS)
        return body
