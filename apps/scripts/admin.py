from django.contrib import admin
from .models import Script


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'script_type', 'is_publish', 'create_date')
    list_filter = ('script_type', 'is_publish', 'create_date')
    search_fields = ('title', 'slug', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('create_date', 'update_date')
    date_hierarchy = 'create_date'

    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'script_type', 'is_publish')
        }),
        ('内容', {
            'fields': ('description', 'code')
        }),
        ('一键命令配置', {
            'fields': ('filename', 'run_cmd'),
            'description': '文件名和下载后的执行命令，系统自动拼接 curl 前缀'
        }),
        ('时间', {
            'fields': ('create_date', 'update_date'),
            'classes': ('collapse',)
        }),
    )
