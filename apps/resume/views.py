from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.core.cache import cache
from django.conf import settings

import markdown

from .models import Resume
from .utils import FlexExtension, BoxExtension, IconExtension


# Create your views here.
class ResumeDetailView(generic.DetailView):
    model = Resume
    template_name = 'resume/detail.html'
    context_object_name = 'resume'

    def get_object(self):
        obj = super(ResumeDetailView, self).get_object()
        # 获取文章更新的时间，判断是否从缓存中取markdown,可以避免每次都转换
        ud = obj.update_date.strftime("%Y%m%d%H%M%S")
        md_key = self.context_object_name + ':markdown:{}:{}'.format(obj.id, ud)
        cache_md = cache.get(md_key)
        if cache_md and settings.DEBUG is False:
            obj.body = cache_md
        else:
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                FlexExtension(),
                BoxExtension(),
                IconExtension()
            ])
            obj.body = md.convert(obj.body)
            cache.set(md_key, obj.body, 3600 * 24 * 30)
        return obj

    def get_queryset(self, **kwargs):
        queryset = super(ResumeDetailView, self).get_queryset()
        return queryset.filter(is_open=True)
