from django.db import models


class TaskScript(models.Model):
    SCRIPT_TYPES = [
        ("python", "Python"),
        ("shell", "Shell"),
    ]

    name = models.CharField(max_length=255, unique=True)
    script = models.TextField()  # 存储 Python/Shell 代码
    script_type = models.CharField(max_length=10, choices=SCRIPT_TYPES, default="python")  # 脚本类型
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.script_type})"

    class Meta:
        verbose_name = '脚本'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']


class EnvironmentVariable(models.Model):
    key = models.CharField(max_length=255, unique=True)  # 变量名
    value = models.TextField()  # 变量值
    description = models.TextField(blank=True, null=True)  # 变量描述，可选
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.key} = {self.value}"

    class Meta:
        verbose_name = '环境变量'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
