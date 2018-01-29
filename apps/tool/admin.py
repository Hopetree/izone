from django.contrib import admin
from .models import ToolCategory, ToolLink


# Register your models here.

@admin.register(ToolLink)
class ToolLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'link', 'order_num','category')


@admin.register(ToolCategory)
class ToolCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order_num')
