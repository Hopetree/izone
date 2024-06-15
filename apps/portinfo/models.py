from django.db import models


class Port(models.Model):
    port_number = models.IntegerField('端口号')
    protocol = models.CharField('协议', max_length=10, help_text='一般填写 TCP，UDP，TCP/UDP 等')
    service_name = models.CharField('服务名称', max_length=100)
    description = models.TextField('描述')
    default_status = models.CharField('默认状态', max_length=20)
    common_usage = models.CharField('使用场景', max_length=200)
    notes = models.TextField('备注', null=True, blank=True)

    class Meta:
        verbose_name = '端口'
        verbose_name_plural = verbose_name
        ordering = ['port_number']

    def __str__(self):
        return f"{self.port_number}/{self.protocol} - {self.service_name}"
