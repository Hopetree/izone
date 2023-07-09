import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from django.conf import settings


class Ouser(AbstractUser):
    link = models.URLField('个人网址', blank=True, help_text='提示：网址必须填写以http开头的完整形式')
    avatar = ProcessedImageField(upload_to='avatar/upload/%Y/%m/%d/%H-%M-%S',
                                 default='avatar/default/default.png',
                                 verbose_name='头像',
                                 processors=[ResizeToFill(80, 80)]
                                 )

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.username
