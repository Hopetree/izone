from django.contrib import admin
from .models import (ArticleComment, Notification, SystemNotification)


@admin.register(ArticleComment)
class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'create_date'
    list_display = ('id', 'author', 'belong', 'create_date', 'show_content')
    list_filter = ('author', 'belong',)
    ordering = ('-id',)
    # 设置需要添加a标签的字段
    list_display_links = ('id', 'show_content')
    search_fields = ('author__username', 'belong__title')

    # 使用方法来自定义一个字段，并且给这个字段设置一个名称
    def show_content(self, obj):
        return obj.content if len(obj.content) < 30 else f'{obj.content[:30]}...'

    show_content.short_description = '评论内容'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    date_hierarchy = 'create_date'
    list_display = ('id', 'create_p', 'create_date', 'comment', 'is_read')
    list_filter = ('create_p', 'is_read',)
    search_fields = ('create_p__username', 'comment__content')

    # 允许直接编辑的字段，对于布尔值的字段，这个非常有用
    list_editable = ('is_read',)


@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    date_hierarchy = 'create_date'
    list_display = ('title', 'get_users', 'create_date', 'show_content', 'is_read')
    list_filter = ('get_p', 'is_read',)
    search_fields = ('title',)

    # 允许直接编辑的字段，对于布尔值的字段，这个非常有用
    list_editable = ('is_read',)

    filter_horizontal = ('get_p',)  # 给多选增加一个左右添加的框

    # 使用方法来自定义一个字段，并且给这个字段设置一个名称
    def show_content(self, obj):
        return obj.content if len(obj.content) < 30 else f'{obj.content[:30]}...'

    def get_users(self, obj):
        return ", ".join([user.username for user in obj.get_p.all()])

    get_users.short_description = '收信人'

    show_content.short_description = '推送内容'
