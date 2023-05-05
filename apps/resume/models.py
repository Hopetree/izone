from django.db import models
from django.conf import settings
from django.shortcuts import reverse


# Create your models here.

class ResumeTemplate(models.Model):
    name = models.CharField('模板名称', max_length=20)
    description = models.TextField('描述', max_length=240)
    content = models.TextField('css内容')

    class Meta:
        verbose_name = '简历模板'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name


# 个人简历
class Resume(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='作者',
                               on_delete=models.PROTECT)
    title = models.CharField(max_length=150, verbose_name='简历标题')
    body = models.TextField(verbose_name='简历内容')
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_date = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    slug = models.SlugField('访问地址', unique=True)
    is_open = models.BooleanField('是否公开', default=False)

    template = models.ForeignKey(ResumeTemplate, verbose_name='简历模板', on_delete=models.PROTECT)

    class Meta:
        verbose_name = '个人简历'
        verbose_name_plural = verbose_name
        ordering = ['-create_date']

    def __str__(self):
        if len(self.title) > 20:
            return self.title[:20] + '...'
        return self.title

    def get_absolute_url(self):
        return reverse('resume:detail', kwargs={'slug': self.slug})
