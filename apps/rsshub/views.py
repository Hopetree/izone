import requests
from django.shortcuts import render
from django.core.cache import cache

from .utils import (get_juejin_hot,
                    get_cnblogs_pick)


# Create your views here.

def juejin_hot_articles(request, type_id, category_id):
    """
    将type和category参数抽离出来，跟掘金的ID对应
    @param request:
    @param type_id:
    @param category_id:
    @return:
    """
    type_dict = {
        'hot': ('hot', '掘金文章榜', 'articles'),
        'collect': ('collect', '掘金收藏榜', 'collected-articles')
    }
    category_dict = {
        'all': ('1', '综合'),
        'backend': ('6809637769959178254', '后端'),
        'frontend': ('6809637767543259144', '前端'),
        'android': ('6809635626879549454', 'Android'),
        'ios': ('6809635626661445640', 'IOS'),
        'ai': ('6809637773935378440', '人工智能'),
        'tool': ('6809637771511070734', '开发工具'),
        'code': ('6809637776263217160', '代码人生'),
        'read': ('6809637772874219534', '阅读')
    }
    if not type_dict.get(type_id) or not category_dict.get(category_id):
        return render(request, '404.html', status=404)

    redis_key = f'rss:juejin:{type_id}:{category_id}'
    redis_value = cache.get(redis_key)
    if redis_value:
        context = redis_value
    else:
        type_value, category_value = type_dict[type_id], category_dict[category_id]
        context = get_juejin_hot(type_value[0], category_value[0])
        title = f'{type_value[1]} ‧ {category_value[1]}'
        if category_id == 'all':
            link = f'https://juejin.cn/hot/{type_value[2]}'
        else:
            link = f'https://juejin.cn/hot/{type_value[2]}/{category_value[0]}'
        context['title'] = title
        context['link'] = link

        cache.set(redis_key, context, 3600 * 2)
    return render(request, 'rsshub/rss.xml', context=context, content_type='application/xml')


def cnblogs_pick(request):
    redis_key = f'rss:cnblogs:pick'
    redis_value = cache.get(redis_key)
    if redis_value:
        context = redis_value
    else:
        context = get_cnblogs_pick()
        context['title'] = '博客园 ‧ 精华博文'
        context['link'] = 'https://www.cnblogs.com/pick/'
        cache.set(redis_key, context, 3600 * 2)
    return render(request, 'rsshub/rss.xml', context=context, content_type='application/xml')
