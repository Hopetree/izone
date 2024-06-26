import uuid

from django.db import models
from django.urls import reverse

from .utils import AESCipher


# Create your models here.

class MonitorServer(models.Model):
    name = models.CharField('名称', max_length=30, unique=True, help_text='用于看板中显示')
    interval = models.IntegerField('上报间隔', default=5,
                                   help_text='上报间隔时间，超过这个时间的两倍还没有更新数据就标记为离线状态，单位：秒')
    sort_order = models.IntegerField('排序', default=99, help_text='自定义排序依据')
    push_url = models.CharField('推送地址', max_length=60,
                                help_text='客户端推送的地址，为了支持代理推送或者本地推送')
    username = models.CharField('用户名', max_length=10, unique=True,
                                help_text='推送用户名，唯一')
    password = models.CharField('密码', max_length=10, unique=True,
                                help_text='第一次添加后自动生成密钥，更改后会重新生成密钥')
    secret_key = models.CharField("加密Key", max_length=64, blank=True, null=True,
                                  help_text='保存后自动生成')
    secret_value = models.CharField("密钥", max_length=256, blank=True, null=True,
                                    help_text='保存后自动生成')
    data = models.TextField('上报数据', blank=True, null=True, help_text='json格式')
    active = models.BooleanField('是否有效', help_text='用来过滤，无效的不显示', default=True)
    alarm = models.BooleanField('是否告警', help_text='默认不告警', default=False)

    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_date = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        verbose_name = '监控服务'
        verbose_name_plural = verbose_name
        ordering = ['sort_order']

    def __str__(self):
        return self.name

    @staticmethod
    def get_absolute_url():
        return reverse('monitor:index')

    def save(self, *args, **kwargs):
        if not self.pk or self._fields_have_changed(['username', 'password', 'push_url']):
            # 如果是首次添加数据或者密码字段发生变化，则生成随机32位密码
            secret_key = str(uuid.uuid4()).replace('-', '')[:32]
            plain_text = f'{self.username}::{self.password}::{self.push_url}'
            cipher = AESCipher(secret_key)
            secret_value = cipher.encrypt(plain_text)
            self.secret_value = secret_value
            self.secret_key = secret_key
        super().save(*args, **kwargs)

    def _fields_have_changed(self, fields):
        if self.pk:
            # 如果是更新数据，则检查指定字段是否发生变化
            original_instance = MonitorServer.objects.get(pk=self.pk)
            for field in fields:
                if getattr(self, field) != getattr(original_instance, field):
                    return True
            return False
        return True  # 如果是首次添加数据，返回 True，表示字段已更改
