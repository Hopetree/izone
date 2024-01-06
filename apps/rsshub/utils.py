# -*- coding: utf-8 -*-
from datetime import datetime
import pytz

import requests


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
