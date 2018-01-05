from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .apis.bd_push import push_urls

# Create your views here.

def Toolview(request):
    return render(request,'tool/tool.html')

def BD_pushview(request):
    return render(request,'tool/bd_push.html')

@login_required
@require_POST
def bd_api_view(request):
    if request.is_ajax():
        data = request.POST
        url = data.get('url')
        urls = data.get('url_list')
        info = push_urls(url,urls)
        return JsonResponse({'msg':info})
    return JsonResponse({'msg':'miss'})

