import json

from celery import current_app
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from django_celery_beat.models import PeriodicTask


def is_admin(user):
    return user.is_authenticated and user.is_staff  # 确保用户为管理员


@user_passes_test(is_admin)
def run_task(request):
    # tasks = PeriodicTask.objects.filter(enabled=True) # 只返回启用的任务
    tasks = PeriodicTask.objects.all()
    context = {'tasks': tasks}
    return render(request, 'blog/runTask.html', context=context)


@user_passes_test(is_admin)
def execute_task(request):
    if request.method == 'POST':
        # 获取任务名称和参数
        task_name = request.POST.get('task_name')
        args = request.POST.get('args', '[]')  # args 应该是 JSON 格式的字符串
        kwargs = request.POST.get('kwargs', '{}')  # kwargs 应该是 JSON 格式的字符串

        if not task_name:
            return JsonResponse({'error': 'Task name is required'}, status=400)

        try:
            # 将 JSON 字符串转换为 Python 对象
            args = json.loads(args)
            kwargs = json.loads(kwargs)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format for args or kwargs'}, status=400)

        if not isinstance(args, list) or not isinstance(kwargs, dict):
            return JsonResponse({'error': 'Invalid type args or kwargs'}, status=400)

        # 使用 send_task 动态执行任务
        result = current_app.send_task(task_name, args=args, kwargs=kwargs)

        # 返回任务 ID 和状态
        return JsonResponse({
            'message': 'Task executed',
            'task_id': result.id,
            'task_status': result.status
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)
