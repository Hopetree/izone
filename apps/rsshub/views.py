import requests
from django.shortcuts import render

from .utils import RSSResponse


# Create your views here.

def juejin_hot_articles(request):
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
    return render(request, 'rsshub/rss.xml', context=rss.as_dict(), content_type='application/xml')
