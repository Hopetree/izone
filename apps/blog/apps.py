from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'blog'
    verbose_name = '博客管理'

    def ready(self):
        from . import signals  # 导入信号处理程序模块
