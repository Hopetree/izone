from django.shortcuts import render
from django.http import JsonResponse
from django.utils.html import mark_safe
from django.core.cache import cache
from .apis.bd_push import push_urls, get_urls
from .apis.useragent import get_user_agent
from .apis.docker_search import DockerSearch
from .apis.word_cloud import jieba_word_cloud
from .utils import IMAGE_LIST

import re
import markdown


# Create your views here.


def Toolview(request):
    return render(request, 'tool/tool.html')


# 百度主动推送
def BD_pushview(request):
    if request.is_ajax() and request.method == "POST":
        data = request.POST
        url = data.get('url')
        urls = data.get('url_list')
        info = push_urls(url, urls)
        return JsonResponse({'msg': info})
    return render(request, 'tool/bd_push.html')


# 百度主动推送升级版，提取sitemap链接推送
def BD_pushview_site(request):
    if request.is_ajax() and request.method == "POST":
        data = request.POST
        url = data.get('url')
        map_url = data.get('map_url')
        urls = get_urls(map_url)
        if urls == 'miss':
            info = "{'error':404,'message':'sitemap地址请求超时，请检查链接地址！'}"
        elif urls == '':
            info = "{'error':400,'message':'sitemap页面没有提取到有效链接，sitemap格式不规范。'}"
        else:
            info = push_urls(url, urls)
        return JsonResponse({'msg': info})
    return render(request, 'tool/bd_push_site.html')


# 在线正则表达式
def regexview(request):
    if request.is_ajax() and request.method == "POST":
        data = request.POST
        texts = data.get('texts')
        regex = data.get('r')
        key = data.get('key')
        try:
            lis = re.findall(r'{}'.format(regex), texts)
        except Exception:
            lis = []
        num = len(lis)
        if key == 'url' and num:
            script_tag = '''<script>$(".re-result p").children("a").attr({target:"_blank",rel:"noopener noreferrer"});</script>'''
            result = '<br>'.join(['[{}]({})'.format(i, i) for i in lis])
        else:
            script_tag = ''
            info = '\n'.join(lis)
            result = "匹配到&nbsp;{}&nbsp;个结果：\n".format(
                num) + "```\n" + info + "\n```"
        result = markdown.markdown(result,
                                   extensions=[
                                       'markdown.extensions.extra',
                                       'markdown.extensions.codehilite',
                                   ])
        return JsonResponse({
            'result': mark_safe(result + script_tag),
            'num': num
        })
    return render(request, 'tool/regex.html')


# 生成请求头
def useragent_view(request):
    if request.is_ajax() and request.method == "POST":
        data = request.POST
        d_lis = data.get('d_lis')
        os_lis = data.get('os_lis')
        n_lis = data.get('n_lis')
        d = d_lis.split(',') if len(d_lis) > 0 else None
        os = os_lis.split(',') if len(os_lis) > 0 else None
        n = n_lis.split(',') if len(n_lis) > 0 else None
        result = get_user_agent(os=os, navigator=n, device_type=d)
        return JsonResponse({'result': result})
    return render(request, 'tool/useragent.html')


# HTML特殊字符对照表
def html_characters(request):
    return render(request, 'tool/characters.html')


# docker镜像查询
def docker_search_view(request):
    if request.is_ajax() and request.method == "POST":
        data = request.POST
        name = data.get('name')
        # 只有名称在常用镜像列表中的搜索才使用缓存，可以避免对名称的过滤
        if name in IMAGE_LIST:
            cache_key = 'tool_docker_search_' + name
            cache_value = cache.get(cache_key)
            if cache_value:
                res = cache_value
            else:
                ds = DockerSearch(name)
                res = ds.main()
                total = res.get('total')
                if total and total >= 20:
                    # 将查询到超过20条镜像信息的资源缓存一天
                    cache.set(cache_key, res, 60 * 60 * 24)
        else:
            ds = DockerSearch(name)
            res = ds.main()
        return JsonResponse(res, status=res['status'])
    return render(request, 'tool/docker_search.html')


def editor_view(request):
    return render(request, 'tool/editor.html')


# 词云图
def word_cloud(request):
    if request.is_ajax() and request.method == "POST":
        data = request.POST
        text = data.get('text')
        stop_text = data.get('stop_text')
        res = jieba_word_cloud(text, stop_text)
        return JsonResponse(res)
    return render(request, 'tool/word_cloud.html')
