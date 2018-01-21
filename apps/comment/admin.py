from django.contrib import admin
from .models import ArticleComment, Notification


@admin.register(ArticleComment)
class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'create_date'
    list_display = ('id', 'author', 'belong', 'create_date', 'parent', 'rep_to')
    list_filter = ('author', 'belong',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    date_hierarchy = 'create_date'
    list_display = ('id', 'create_p', 'create_date', 'comment', 'is_read')
    list_filter = ('create_p', 'is_read',)
