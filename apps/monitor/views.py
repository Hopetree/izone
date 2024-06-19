import datetime
import json
import random

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from blog.utils import add_views
from .utils import Server
from .models import MonitorServer


# Create your views here.
def is_admin(user):
    return user.is_authenticated and user.is_staff


def index(request):
    if request.user.is_staff:
        return render(request, 'monitor/index.html')
    return render(request, '403.html')


@add_views('monitor:demo', '服务监控Demo')
def demo(request):
    return render(request, 'monitor/demo.html')


def get_server_list_for_demo(request):
    data = {'code': 0, 'error': '', 'message': '', 'data': {}}
    sli = ['darwin', 'redhat', 'debian', 'ubuntu',
           'centos', 'windows', '-', 'redhat', 'debian',
           'DSM', 'windows', 'darwin', 'redhat', 'debian']
    server_list = []
    for i in range(1, 12):
        server_data = {
            "interval": 10,
            "uptime": "{} 天".format(random.randint(10, 100)),
            "system": f"linux-3.10.0-1160.99.1.el7.x86_64-x86_64-{sli[i]}-7.9.2009",
            "cpu_cores": i * 2,
            "cpu_model": "AMD Ryzen 7 5700U with Radeon Graphics",
            "cpu": round(random.uniform(0, 100), 1),
            "load_1": round(random.uniform(0, 10), 2),
            "load_5": round(random.uniform(0, 10), 2),
            "load_15": round(random.uniform(0, 10), 2),
            "memory_total": "8.00G",
            "memory_used": "{}G".format(round(random.uniform(0, 6), 2)),
            "swap_total": "2.0G",
            "swap_used": "0.0G",
            "hdd_total": "100G",
            "hdd_used": "{}G".format(round(random.uniform(0, 100), 2)),
            "network_in": "{}K".format(round(random.uniform(0, 100), 1)),
            "network_out": "{}K".format(round(random.uniform(0, 100), 1)),
            "process": random.randint(100, 500),
            "thread": random.randint(500, 1000),
            "tcp": random.randint(1, 50),
            "udp": random.randint(0, 10),
            "memory": round(random.uniform(0, 100), 1),
            "hdd": round(random.uniform(0, 100), 1),
            "status": random.choice(['online', 'offline']),
            "name": f"Node-{str(i).zfill(2)}",
            "version": f"6.23.{i}",
            "client_version": "0.1.0",
            "date": "{}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        }
        server_list.append(server_data)
    server_list[-1]['system'] = 'Unknown'
    data['data']['list'] = server_list
    return JsonResponse(data)


@login_required
@user_passes_test(is_admin)
def get_server_list(request):
    data = {'code': 0, 'error': '', 'message': '', 'data': {}}
    current_time = timezone.now()
    server_list = []
    instance_list = MonitorServer.objects.filter(
        secret_key__isnull=False,
        secret_value__isnull=False,
        data__isnull=False,
        active=True
    )
    for instance in instance_list:
        instance_data = json.loads(instance.data)
        time_difference = current_time - instance.update_date
        seconds_difference = time_difference.total_seconds()
        # 上报时间大于频率的两倍，则判定为离线
        if seconds_difference > instance.interval * 2:
            instance_data['status'] = 'offline'
        else:
            instance_data['status'] = 'online'
        instance_data['name'] = instance.name
        instance_data['date'] = instance.update_date
        instance_data['alarm'] = '是' if instance.alarm else '否'
        # 服务版本，没有就显示null
        instance_data['version'] = instance_data.get('version')
        server_list.append(instance_data)
    data['data']['list'] = server_list
    return JsonResponse(data)


@csrf_exempt
def server_push(request):
    resp_data = {'code': 0, 'error': '', 'message': '', 'data': {}}
    if request.method != 'POST':
        resp_data['code'] = 1
        resp_data['error'] = 'Invalid request method'
        return JsonResponse(resp_data, status=405)
    if request.content_type != 'application/json':
        resp_data['code'] = 1
        resp_data['error'] = 'Unsupported content type'
        return JsonResponse(resp_data, status=415)

    # 缺少请求头直接拒绝
    push_key = request.headers.get('Push-Key')
    push_value = request.headers.get('Push-Value')
    push_username = request.headers.get('Push-Username')
    push_password = request.headers.get('Push-Password')
    if not all([push_key, push_value, push_username, push_password]):
        resp_data['code'] = 1
        resp_data['error'] = 'Headers need: Push-Key,Push-Value,Push-Username,Push-Password '
        return JsonResponse(resp_data, status=400)

    # 检查请求体，有不合规的字段就拒绝
    try:
        json_data = json.loads(request.body)
    except json.JSONDecodeError:
        resp_data['code'] = 1
        resp_data['error'] = 'Invalid JSON data'
        return JsonResponse(resp_data, status=400)
    else:
        server = Server(json_data)
        flag, err = server.check_data()
        if not flag:
            resp_data['code'] = 1
            resp_data['error'] = err
            return JsonResponse(resp_data, status=400)

        # 获取实例，不存在则直接退出
        instance = MonitorServer.objects.filter(
            username=push_username,
            password=push_password,
            secret_key=push_key,
            secret_value=push_value
        ).first()
        if not instance:
            resp_data['code'] = 1
            resp_data['error'] = "Service instance does not exist"
            return JsonResponse(resp_data, status=400)

        # 原始数据处理后存入数据库
        if json_data['uptime'] < 3600:
            uptime_m = json_data['uptime'] // 60
            uptime_s = json_data['uptime'] % 60
            json_data['uptime'] = '{}分{}秒'.format(uptime_m, uptime_s)
        elif json_data['uptime'] < 3600 * 24:
            uptime_h = json_data['uptime'] // 3600
            uptime_m = json_data['uptime'] % 3600 // 60
            json_data['uptime'] = '{}小时{}分'.format(uptime_h, uptime_m)
        else:
            uptime_d = json_data['uptime'] // (3600 * 24)
            uptime_h = json_data['uptime'] % (3600 * 24) // 3600
            json_data['uptime'] = '{}天{}小时'.format(uptime_d, uptime_h)
        memory = round((json_data['memory_used'] / json_data['memory_total']) * 100, 1)
        hdd = round((json_data['hdd_used'] / json_data['hdd_total']) * 100, 1)
        json_data['memory'] = memory  # 内存使用率
        json_data['hdd'] = hdd  # 磁盘使用率
        json_data['cpu'] = round(json_data['cpu'], 1)  # CPU使用率
        json_data['memory_total'] = '{}G'.format(
            round(json_data['memory_total'] / (1024 * 1024 * 1024), 2))
        json_data['memory_used'] = '{}G'.format(
            round(json_data['memory_used'] / (1024 * 1024 * 1024), 2))
        json_data['swap_total'] = '{}G'.format(
            round(json_data['swap_total'] / (1024 * 1024 * 1024), 2))
        json_data['swap_used'] = '{}G'.format(
            round(json_data['swap_used'] / (1024 * 1024 * 1024), 2))
        json_data['hdd_total'] = '{}G'.format(
            round(json_data['hdd_total'] / (1024 * 1024 * 1024), 2))
        json_data['hdd_used'] = '{}G'.format(
            round(json_data['hdd_used'] / (1024 * 1024 * 1024), 2))
        instance.data = json.dumps(json_data, ensure_ascii=False)
        instance.interval = json_data['interval']
        instance.save()
        resp_data['data'] = json_data
        return JsonResponse(resp_data)
