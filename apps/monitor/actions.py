import json
from datetime import datetime


def action_check_host_status(recipient_list=None):
    from django.conf import settings
    from django.core.mail import send_mail
    from .models import MonitorServer

    if not recipient_list:
        return 'No recipient_list, please set it.'

    if hasattr(settings, 'DEFAULT_FROM_EMAIL') and settings.DEFAULT_FROM_EMAIL:
        from_email = settings.DEFAULT_FROM_EMAIL
    else:
        # 如果未设置发件人邮箱，设置为空，直接退出
        return 'Email configuration not set'

    current_date = datetime.now()
    alarm_list = []
    hosts = MonitorServer.objects.filter(
        secret_key__isnull=False,
        secret_value__isnull=False,
        data__isnull=False,
        active=True
    )
    for host in hosts:
        # 转换成分钟
        m = int((current_date - host.update_date).total_seconds() / 60)
        # 多个时间点发送
        if m in [1, 10, 60, 240, 60 * 24]:
            msg = f'警告：节点 {host.name} 离线 {m} 分钟'
            alarm_list.append(msg)
        else:
            continue
    if all([alarm_list, from_email, recipient_list]):
        subject = f'⚠️服务监控告警 {current_date.strftime("%Y-%m-%d %H:%M:%S")}'
        message = '\n'.join(alarm_list)
        ok_num = send_mail(subject, message, from_email, recipient_list)
        return f"Send email ok: {ok_num}"

    return "Not alarm !!!"
