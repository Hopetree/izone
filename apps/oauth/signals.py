# -*- coding: utf-8 -*-
import random
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Ouser


@receiver(pre_save, sender=Ouser)
def generate_avatar(sender, instance, **kwargs):
    if instance._state.adding:
        # 随机选择一个头像地址
        random_avatar = 'avatar/default/default{}.png'.format(random.randint(1, 10))
        instance.avatar = random_avatar
