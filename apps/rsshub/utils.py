# -*- coding: utf-8 -*-
import logging
import re
from datetime import datetime
import pytz

import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)


class RSSResponse(object):
    def __init__(self, title='', link='', items=None):
        self.title = title
        self.link = link
        self.items = items or []
        self.update = datetime.now().astimezone(pytz.timezone('UTC')).strftime(
            "%a, %d %b %Y %H:%M:%S %Z")

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def as_dict(self):
        data = {
            'title': self.title,
            'link': self.link,
            'update': self.update,
            'items': self.items
        }
        return data


# 外呼失败或上游返回空时的短缓存时间，避免上游异常期间每个请求都去重试
RSS_FAIL_CACHE_SECONDS = 60
# 防击穿锁的持有时间，只需覆盖一次外呼的耗时
RSS_LOCK_SECONDS = 15


def _empty_rss(title='', link=''):
    """外呼不可用时的占位 RSS，避免请求 500 或长时间阻塞"""
    return RSSResponse(title=title, link=link).as_dict()


def cached_rss_fetch(cache_key, fetch_func, title='', link='', ttl=3600 * 2):
    """
    带缓存和外呼保护的 RSS 获取。

    - 命中缓存直接返回；
    - 未命中时用 Redis 锁保证只有一个请求真正去外呼，其余并发请求立即拿到占位内容，
      避免上游变慢时（单 gunicorn worker）把整站请求都阻塞住；
    - 外呼异常不再冒泡成 500，而是返回占位内容并短缓存，防止上游故障期间反复重试。
    """
    cached = cache.get(cache_key)
    if cached:
        return cached

    lock_key = cache_key + ':lock'
    # django-redis 的 add 抢到锁返回 True，key 已存在（别人在拉）返回 None，
    # 因此用 not 判断：没抢到锁就立刻返回占位内容，绝不在请求里排队等外呼
    if not cache.add(lock_key, 1, RSS_LOCK_SECONDS):
        return _empty_rss(title=title, link=link)

    try:
        context = fetch_func()
    except Exception:
        logger.exception('rss fetch failed: %s', cache_key)
        context = _empty_rss(title=title, link=link)
        cache.set(cache_key, context, RSS_FAIL_CACHE_SECONDS)
        return context

    if not context.get('items'):
        # 上游这次没有返回有效条目，短缓存一下，避免连续打上游
        cache.set(cache_key, context, RSS_FAIL_CACHE_SECONDS)
        return context

    cache.set(cache_key, context, ttl)
    return context


def get_juejin_hot(type_id, category_id):
    """
    获取掘金热榜文章，根据分类ID获取不同分类的文章
    @param type_id: 类型，hot表示热榜，collect表示收藏榜
    @param category_id: 分类，对应掘金的分类ID
    @return:
    """

    rss = RSSResponse()
    url = 'https://api.juejin.cn/content_api/v1/content/article_rank'
    params = {'type': type_id, 'category_id': category_id}
    response = requests.get(url, params=params, timeout=5, verify=False)
    data = response.json()['data']
    items = []
    for each in data:
        title = each['content']['title']
        link = 'https://juejin.cn/post/' + each['content']['content_id']
        items.append({'title': title, 'link': link})
    rss.items = items
    return rss.as_dict()


def get_cnblogs_pick():
    """
    获取博客园的精华
    @return:
    """
    url = 'https://www.cnblogs.com/pick/'
    try:
        response = requests.get(url, timeout=5, verify=False)
        text = response.text
    except:
        text = ''
    article_list = re.findall('<a class="post-item-title" href="(.*?)" target="_blank">(.*?)</a>',
                              text)
    rss = RSSResponse()
    items = []
    for link, title in article_list:
        items.append({'title': title, 'link': link})
    rss.items = items
    return rss.as_dict()


def get_github_issues(api_url):
    try:
        headers = {
            'User-Agent': 'Awesome-Octocat-App',
            'Accept': 'application/vnd.github+json'
        }
        response = requests.get(api_url, timeout=10, verify=False, headers=headers)
        if response.status_code == 200 and isinstance(response.json(), list):
            issues = response.json()
        else:
            issues = []
    except:
        issues = []
    rss = RSSResponse()
    items = []
    for issue in issues:
        items.append({'title': issue['title'], 'link': issue['html_url']})
    rss.items = items
    return rss.as_dict()


if __name__ == '__main__':
    f = get_github_issues('https://api.github.com/repos/ruanyf/weekly/issues')
    print(f)
