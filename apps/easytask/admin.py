from django.contrib import admin
from django.contrib.admin import widgets
from .models import TaskScript, EnvironmentVariable


@admin.register(TaskScript)
class TaskScriptAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "script_type", "created_at")
    list_filter = ("script_type", "created_at")
    search_fields = ("name", "script")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'script':  # 替换为你的 TextField 字段名
            kwargs['widget'] = widgets.AdminTextareaWidget(attrs={
                'style': 'min-height: 40rem;',  # 设置最小高度
            })
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        ("基本信息", {"fields": ("name", "script_type")}),
        ("脚本内容", {"fields": ("script",)}),
        ("元数据", {"fields": ("created_at",)}),
    )

@admin.register(EnvironmentVariable)
class EnvironmentVariableAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "value", "description", "created_at")  # 添加 description
    search_fields = ("key", "value", "description")  # 允许搜索描述
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    fieldsets = (
        ("环境变量", {"fields": ("key", "value", "description")}),
        ("元数据", {"fields": ("created_at",)}),
    )
