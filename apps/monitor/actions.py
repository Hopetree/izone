import json
from datetime import datetime


def action_check_host_status(recipient_list=None, times=None, ignore_hours=None):
    from django.conf import settings
    from django.core.mail import send_mail
    from .models import MonitorServer

    current_date = datetime.now()

    # 忽略的检查时段，这些时段不检查状态
    # 这个忽略的意义是因为运营商会定期断网更新IP，导致上报失败触发告警，比如电信是4点多断网一段时间
    ignore_hours = ignore_hours or []

    if current_date.hour in ignore_hours:
        return f'Ignore period for {ignore_hours}, do not check.'

    # 可以通过参数传递通知的频率
    times = times or [1, 10, 60, 60 * 4, 60 * 24]

    if not recipient_list:
        return 'No recipient_list, please set it.'

    if hasattr(settings, 'DEFAULT_FROM_EMAIL') and settings.DEFAULT_FROM_EMAIL:
        from_email = settings.DEFAULT_FROM_EMAIL
    else:
        # 如果未设置发件人邮箱，设置为空，直接退出
        return 'Email configuration not set.'

    alarm_list = []
    hosts = MonitorServer.objects.filter(
        secret_key__isnull=False,
        secret_value__isnull=False,
        data__isnull=False,
        active=True,
        alarm=True
    )
    for host in hosts:
        # 转换成分钟
        m = int((current_date - host.update_date).total_seconds() / 60)
        # 多个时间点发送
        if m in times:
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
