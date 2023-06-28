# -*- coding: utf-8 -*-
import time

from celery import shared_task
from markdown import Markdown
from markdown.extensions.toc import TocExtension  # 锚点的拓展
from markdown.extensions.codehilite import CodeHiliteExtension
from django.core.cache import cache
from django.utils.text import slugify

from blog.models import Article
from blog.utils import CustomHtmlFormatter


@shared_task
def simple_test_task(x, y):
    time.sleep(5)
    return x + y


@shared_task
def update_article_cache():
    """
    更新所有文章的缓存，缓存格式跟文章视图保持一致
    @return:
    """
    data = {'total': 0, 'done': 0}
    for obj in Article.objects.all():
        data['total'] += 1
        ud = obj.update_date.strftime("%Y%m%d%H%M%S")
        md_key = f'article:markdown:{obj.id}:{ud}'
        cache_md = cache.get(md_key)
        if not cache_md:
            md = Markdown(extensions=[
                'markdown.extensions.extra',
                CodeHiliteExtension(pygments_formatter=CustomHtmlFormatter),
                TocExtension(slugify=slugify),
            ])
            cache.set(md_key, (md.convert(obj.body), md.toc), 3600 * 24 * 7)
            data['done'] += 1
    return data
