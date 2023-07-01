# -*- coding: utf-8 -*-
import requests
from markdown import Markdown
from markdown.extensions.toc import TocExtension  # 锚点的拓展
from markdown.extensions.codehilite import CodeHiliteExtension
from django.core.cache import cache
from django.utils.text import slugify

from blog.models import Article, FriendLink
from blog.utils import CustomHtmlFormatter


def update_article_cache():
    """
    更新所有文章的缓存，缓存格式跟文章视图保持一致
    @return:
    """
    total_num, done_num = 0, 0
    # 查询到所有缓存的key
    keys = cache.keys('article:markdown:*')
    for obj in Article.objects.all():
        total_num += 1
        ud = obj.update_date.strftime("%Y%m%d%H%M%S")
        md_key = f'article:markdown:{obj.id}:{ud}'
        # 设置不存在的缓存
        if md_key not in keys:
            md = Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown_checklist.extension',
                CodeHiliteExtension(pygments_formatter=CustomHtmlFormatter),
                TocExtension(slugify=slugify),
            ])
            # 设置过期时间的时候分散时间，不要设置成同一时间
            cache.set(md_key, (md.convert(obj.body), md.toc), 3600 * 24 + 10 * done_num)
            done_num += 1
    data = {'total': total_num, 'done': done_num}
    return data


def check_friend_links():
    """
    检查友链:
        1、检查当前显示的友链，请求友链，将非200的友链标记为不显示
        2、检查当前不显示的友链，请求友链，将200返回的标记为显示
    @return:
    """

    def get_link_status(url):
        try:
            status_code = requests.get(url, timeout=5, verify=False).status_code
        except Exception:
            status_code = 500
        return status_code

    active_num = 0
    to_not_show = 0
    to_show = 0
    active_friend_list = FriendLink.objects.filter(is_active=True)
    for active_friend in active_friend_list:
        active_num += 1
        if active_friend.is_show is True:
            code = get_link_status(active_friend.link)
            if code != 200:
                active_friend.is_show = False
                active_friend.save(update_fields=['is_show'])
                to_not_show += 1
        else:
            code = get_link_status(active_friend.link)
            if code == 200:
                active_friend.is_show = True
                active_friend.save(update_fields=['is_show'])
                to_show += 1
    data = {'active_num': active_num, 'to_not_show': to_not_show, 'to_show': to_show}
    return data
