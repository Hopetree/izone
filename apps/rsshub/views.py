import requests
from django.shortcuts import render
from django.core.cache import cache

from .utils import RSSResponse


# Create your views here.

def juejin_hot_articles(request):
    redis_key = f'rss:{juejin_hot_articles.__name__}'
    redis_value = cache.get(redis_key)
    if redis_value:
        context = redis_value
    else:
        rss = RSSResponse('掘金热榜 ‧ 综合', 'https://juejin.cn/hot/articles')
        url = 'https://api.juejin.cn/content_api/v1/content/article_rank'
        params = {'type': 'hot', 'category_id': '1'}
        response = requests.get(url, params=params, timeout=5, verify=False)
        data = response.json()['data']
        items = []
        for each in data:
            title = each['content']['title']
            link = 'https://juejin.cn/post/' + each['content']['content_id']
            items.append({'title': title, 'link': link})
        rss.items = items
        context = rss.as_dict()
        cache.set(redis_key, context, 3600 * 2)
    return render(request, 'rsshub/rss.xml', context=context, content_type='application/xml')
