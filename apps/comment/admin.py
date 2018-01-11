from django.contrib import admin
from .models import ArticleComment

@admin.register(ArticleComment)
class CommentAdmin(admin.ModelAdmin):

    date_hierarchy = 'create_date'
    list_display = ('id','author','belong','create_date','parent','rep_to')
    list_filter = ('author','belong',)
