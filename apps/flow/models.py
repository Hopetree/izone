from django.db import models

class Process(models.Model):
    name = models.CharField('流程名称', max_length=100)
    xml_content = models.TextField('XML内容')
    tags = models.TextField('标签', default='[]')  # 使用TextField存储JSON字符串
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['-create_time']
        verbose_name = '流程'
        verbose_name_plural = verbose_name
