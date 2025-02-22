from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
import json
from blog.utils import add_views
from .models import Process

# Create your views here.

# 原有的视图函数保持不变
@add_views('flow:index', '流程设计')
def index(request):
    is_admin = request.user.is_superuser
    return render(request, 'flow/index.html', {'is_admin': is_admin})

def create(request):
    is_admin = request.user.is_superuser
    return render(request, 'flow/create.html', {'is_admin': is_admin})

def edit(request):
    is_admin = request.user.is_superuser
    return render(request, 'flow/edit.html', {'is_admin': is_admin})

def view(request):
    is_admin = request.user.is_superuser
    return render(request, 'flow/view.html', {'is_admin': is_admin})

# 新增 API 接口
# 修改 API 接口，添加必要的导入和装饰器
@staff_member_required(login_url='admin:login')  # 添加登录重定向
@require_http_methods(["GET"])
def process_list(request):
    processes = Process.objects.all()
    data = [{
        'id': p.id,
        'name': p.name,
        'tags': json.loads(p.tags),
        'createTime': int(p.create_time.timestamp() * 1000),  # 修正时间戳转换
        'updateTime': int(p.update_time.timestamp() * 1000)   # 修正时间戳转换
    } for p in processes]
    return JsonResponse({'processes': data})

@staff_member_required(login_url='admin:login')
@require_http_methods(["GET"])
def process_detail(request, process_id):
    try:
        process = Process.objects.get(id=process_id)
        data = {
            'id': process.id,
            'name': process.name,
            'xml': process.xml_content,
            'tags': json.loads(process.tags),
            'createTime': int(process.create_time.timestamp() * 1000),
            'updateTime': int(process.update_time.timestamp() * 1000)
        }
        return JsonResponse(data)
    except Process.DoesNotExist:
        return JsonResponse({'error': '流程不存在'}, status=404)

@staff_member_required(login_url='admin:login')
@require_http_methods(["POST"])
def process_create(request):
    try:
        data = json.loads(request.body)
        process = Process.objects.create(
            name=data.get('name', '未命名流程'),
            xml_content=data.get('xml', ''),
            tags=json.dumps(data.get('tags', []))
        )
        return JsonResponse({
            'id': process.id,
            'name': process.name,
            'tags': json.loads(process.tags),
            'createTime': int(process.create_time.timestamp() * 1000),
            'updateTime': int(process.update_time.timestamp() * 1000)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@staff_member_required(login_url='admin:login')
@require_http_methods(["POST"])
def process_update(request, process_id):
    try:
        process = Process.objects.get(id=process_id)
        data = json.loads(request.body)
        
        if 'name' in data:
            process.name = data['name']
        if 'xml' in data:
            process.xml_content = data['xml']
        if 'tags' in data:
            process.tags = json.dumps(data['tags'])
            
        process.save()
        return JsonResponse({
            'id': process.id,
            'name': process.name,
            'tags': json.loads(process.tags),
            'createTime': int(process.create_time.timestamp() * 1000),
            'updateTime': int(process.update_time.timestamp() * 1000)
        })
    except Process.DoesNotExist:
        return JsonResponse({'error': '流程不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@staff_member_required(login_url='admin:login')
@require_http_methods(["POST"])
def process_delete(request, process_id):
    try:
        process = Process.objects.get(id=process_id)
        process.delete()
        return JsonResponse({'success': True})
    except Process.DoesNotExist:
        return JsonResponse({'error': '流程不存在'}, status=404)
