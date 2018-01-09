from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .apis.bd_push import push_urls, get_urls
from .apis.links_test import check_links

import re

# Create your views here.

def Toolview(request):
    return render(request,'tool/tool.html')

# 百度主动推送
def BD_pushview(request):
    return render(request,'tool/bd_push.html')

@require_POST
def bd_api_view(request):
    if request.is_ajax():
        data = request.POST
        url = data.get('url')
        urls = data.get('url_list')
        info = push_urls(url,urls)
        return JsonResponse({'msg':info})
    return JsonResponse({'msg':'miss'})

# 百度主动推送升级版，提取sitemap链接推送
def BD_pushview_site(request):
    return render(request, 'tool/bd_push_site.html')

@require_POST
def bd_api_site(request):
    if request.is_ajax():
        data = request.POST
        url = data.get('url')
        map_url = data.get('map_url')
        urls = get_urls(map_url)
        if urls == 'miss':
            info = "{'error':404,'message':'sitemap地址请求超时，请检查链接地址！'}"
        elif urls == '':
            info = "{'error':400,'message':'sitemap页面没有提取到有效链接，sitemap格式不规范。'}"
        else:
            info = push_urls(url,urls)
        return JsonResponse({'msg':info})
    return JsonResponse({'msg':'miss'})

# 友链检测
def Link_testview(request):
    return render(request, 'tool/link_test.html')

@require_POST
def Link_test_api(request):
    if request.is_ajax():
        data = request.POST
        p = data.get('p')
        urls = data.get('urls')
        info = check_links(urls,p)
        return JsonResponse(info)
    return JsonResponse({'msg': 'miss'})

# 在线正则表达式
def regexview(request):
    return render(request, 'tool/regex.html')

@require_POST
def regex_api(request):
    if request.is_ajax():
        data = request.POST
        texts = data.get('texts')
        regex = data.get('r')
        result = re.findall(r'{}'.format(regex),texts)
        return JsonResponse({'result':result})
    return JsonResponse({'msg': 'miss'})

