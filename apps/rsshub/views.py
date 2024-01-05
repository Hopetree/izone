import requests
from django.shortcuts import render
from django.core.cache import cache

from .utils import get_juejin_hot_article


# Create your views here.

def juejin_hot_articles(request):
    redis_key = f'rss:{juejin_hot_articles.__name__}'
    redis_value = cache.get(redis_key)
    if redis_value:
        context = redis_value
    else:
        context = get_juejin_hot_article(1)
        cache.set(redis_key, context, 3600 * 2)
    return render(request, 'rsshub/rss.xml', context=context, content_type='application/xml')
