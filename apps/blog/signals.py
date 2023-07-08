# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.urls import reverse

from .models import FriendLink
from comment.models import SystemNotification
from oauth.models import Ouser


@receiver(post_save, sender=FriendLink)
def friend_link_create_signal(sender, instance, created, **kwargs):
    """
    创建新的友情链接则自带给管理员推送审核消息
    @param sender:
    @param instance:
    @param created:
    @param kwargs:
    @return:
    """
    # 判断是否是第一次生成
    if created:
        superuser = Ouser.objects.filter(is_superuser=True)
        title = f'增加一个新的{instance._meta.verbose_name}:{instance.name}'
        admin_url = reverse('admin:blog_friendlink_change', args=[instance.id])
        content = f'<p><a href="{admin_url}">友链地址：{instance.link}，' \
                  f'描述：{instance.description}，待管理员审核！！！</a></p>'
        new_notify = SystemNotification(title=title, content=content)
        new_notify.save()  # 保存实例

        # 在保存实例后，将关联对象添加到多对多关系中
        new_notify.get_p.set(superuser)
