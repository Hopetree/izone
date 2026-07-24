from django.db import models
from django.urls import reverse


class Script(models.Model):
    SCRIPT_TYPES = (
        ('shell', 'Shell'),
        ('python', 'Python'),
    )

    title = models.CharField(max_length=150, verbose_name='标题')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='URL标识')
    description = models.TextField(verbose_name='说明文档（Markdown）')
    code = models.TextField(verbose_name='脚本代码')
    script_type = models.CharField(
        max_length=10, choices=SCRIPT_TYPES, default='shell',
        verbose_name='脚本类型'
    )
    filename = models.CharField(
        max_length=100, verbose_name='下载文件名',
        help_text='例如 install-docker.sh'
    )
    run_cmd = models.CharField(
        max_length=500, verbose_name='执行命令',
        help_text='下载后的执行命令，例如 /bin/bash install-docker.sh -m'
    )
    is_publish = models.BooleanField(default=False, verbose_name='是否发布')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '脚本'
        verbose_name_plural = verbose_name
        ordering = ['-create_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('scripts:detail', kwargs={'slug': self.slug})

    def get_raw_url(self):
        return reverse('scripts:raw', kwargs={'slug': self.slug})

    @property
    def full_command(self):
        """拼接完整的一键命令"""
        base = f"curl -o {self.filename} https://tendcode.com{self.get_raw_url()}"
        if self.run_cmd:
            return f"{base} && {self.run_cmd}"
        return base

    @property
    def language_class(self):
        """返回 Pygments 识别的语言标识"""
        return {
            'shell': 'bash',
            'python': 'python',
        }.get(self.script_type, 'text')
