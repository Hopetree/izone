from django.apps import apps
from django.conf import settings
from django.contrib import admin

from .models import Resume, ResumeTemplate


# Register your models here.

@admin.register(ResumeTemplate)
class ResumeTemplateAdmin(admin.ModelAdmin):
    # 在查看修改的时候显示的属性，第一个字段带有<a>标签，所以最好放标题
    list_display = ('id', 'name', 'description')

    # 设置需要添加<a>标签的字段
    list_display_links = ('name',)

    # 限制用户权限，只能超管可以编辑
    def get_queryset(self, request):
        qs = super(ResumeTemplateAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return None


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    # 这个的作用是给出一个筛选机制，一般按照时间比较好
    date_hierarchy = 'create_date'

    # 在查看修改的时候显示的属性，第一个字段带有<a>标签，所以最好放标题
    list_display = ('id', 'title', 'author', 'is_open', 'slug', 'create_date', 'update_date')

    # 设置需要添加<a>标签的字段
    list_display_links = ('title',)

    # 激活过滤器，这个很有用
    list_filter = ('create_date', 'is_open')

    # 限制用户权限，只能看到自己编辑的简历
    def get_queryset(self, request):
        qs = super(ResumeAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        User = apps.get_model(settings.AUTH_USER_MODEL)
        if db_field.name == 'author':
            if request.user.is_superuser:
                kwargs['queryset'] = User.objects.filter(is_staff=True, is_active=True)
            else:
                kwargs['queryset'] = User.objects.filter(id=request.user.id)
        return super(ResumeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
