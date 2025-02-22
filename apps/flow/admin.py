from django.contrib import admin
from .models import Process

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_time', 'update_time')
    list_filter = ('create_time', 'update_time')
    search_fields = ('name',)
    readonly_fields = ('create_time', 'update_time')
    ordering = ('-create_time',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # 编辑时
            return self.readonly_fields
        return ()  # 新建时
