from django.db import models


# Create your models here.

class ToolCategory(models.Model):
    name = models.CharField('网站分类名称', max_length=20)
    order_num = models.IntegerField('序号', default=99, help_text='序号可以用来调整顺序，越小越靠前')

    class Meta:
        verbose_name = '工具分类'
        verbose_name_plural = verbose_name
        ordering = ['order_num', 'id']

    def __str__(self):
        return self.name

class ToolLink(models.Model):
    name = models.CharField('网站名称', max_length=20)
    description = models.CharField('网站描述', max_length=100)
    link = models.URLField('网站链接')
    order_num = models.IntegerField('序号', default=99, help_text='序号可以用来调整顺序，越小越靠前')
    category = models.ForeignKey(ToolCategory, verbose_name='网站分类',blank=True,null=True)

    class Meta:
        verbose_name = '推荐工具'
        verbose_name_plural = verbose_name
        ordering = ['order_num', 'id']

    def __str__(self):
        return self.name


