from django.contrib import admin
from .models import MonitorServer


# Register your models here.
@admin.register(MonitorServer)
class MonitorServerViewAdmin(admin.ModelAdmin):
    list_display = ('name', 'interval', 'sort_order', 'username', 'secret_key')
    ordering = ('sort_order',)
    list_editable = ('sort_order',)

    readonly_fields = ('secret_key', 'secret_value', 'data')
