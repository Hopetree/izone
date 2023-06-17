from django.apps import AppConfig


class CommentConfig(AppConfig):
    name = 'comment'
    verbose_name = '评论管理'

    def ready(self):
        from . import signals  # 导入信号处理程序模块
