from django.contrib import admin
from .models import ArticleComment, Notification


@admin.register(ArticleComment)
class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'create_date'
    list_display = ('id', 'author', 'belong', 'create_date', 'show_content')
    list_filter = ('author', 'belong',)
    ordering = ('-id',)
    # 设置需要添加a标签的字段
    list_display_links = ('id', 'show_content')

    # 使用方法来自定义一个字段，并且给这个字段设置一个名称
    def show_content(self, obj):
        return obj.content[:30]

    show_content.short_description = '评论内容'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    date_hierarchy = 'create_date'
    list_display = ('id', 'create_p', 'create_date', 'comment', 'is_read')
    list_filter = ('create_p', 'is_read',)
