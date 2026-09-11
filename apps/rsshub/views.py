from django.shortcuts import render

from .utils import (get_juejin_hot,
                    get_cnblogs_pick,
                    get_github_issues,
                    cached_rss_fetch)


# Create your views here.

JUEJIN_TYPE_DICT = {
    'hot': ('hot', '掘金文章榜', 'articles'),
    'collect': ('collect', '掘金收藏榜', 'collected-articles')
}
JUEJIN_CATEGORY_DICT = {
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


def juejin_hot_articles(request, type_id, category_id):
    """
    将type和category参数抽离出来，跟掘金的ID对应
    @param request:
    @param type_id:
    @param category_id:
    @return:
    """
    if not JUEJIN_TYPE_DICT.get(type_id) or not JUEJIN_CATEGORY_DICT.get(category_id):
        return render(request, '404.html', status=404)

    type_value = JUEJIN_TYPE_DICT[type_id]
    category_value = JUEJIN_CATEGORY_DICT[category_id]
    title = f'{type_value[1]} ‧ {category_value[1]}'
    if category_id == 'all':
        link = f'https://juejin.cn/hot/{type_value[2]}'
    else:
        link = f'https://juejin.cn/hot/{type_value[2]}/{category_value[0]}'

    def fetch():
        context = get_juejin_hot(type_value[0], category_value[0])
        context['title'] = title
        context['link'] = link
        return context

    context = cached_rss_fetch(
        f'rss:juejin:{type_id}:{category_id}', fetch, title=title, link=link
    )
    return render(request, 'rsshub/rss.xml', context=context, content_type='application/xml')


def cnblogs_pick(request):
    title = '博客园 ‧ 精华博文'
    link = 'https://www.cnblogs.com/pick/'

    def fetch():
        context = get_cnblogs_pick()
        context['title'] = title
        context['link'] = link
        return context

    context = cached_rss_fetch('rss:cnblogs:pick', fetch, title=title, link=link)
    return render(request, 'rsshub/rss.xml', context=context, content_type='application/xml')


def github_issues_ryf(request):
    api_issues_url = 'https://api.github.com/repos/ruanyf/weekly/issues'
    title = '阮一峰周刊 issues'
    link = 'https://github.com/ruanyf/weekly/issues'

    def fetch():
        context = get_github_issues(api_issues_url)
        context['title'] = title
        context['link'] = link
        return context

    context = cached_rss_fetch('rss:github-issues:ruanyf:weekly', fetch, title=title, link=link)
    return render(request, 'rsshub/rss.xml', context=context, content_type='application/xml')

