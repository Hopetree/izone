from django.core.exceptions import PermissionDenied
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

    def get_object(self, queryset=None):
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

    def dispatch(self, request, *args, **kwargs):
        """
        检查当前登录的用户是否与模型实例中的用户匹配。如果匹配，说明当前用户是该模型实例的所有者，可以访问页面。
        否则，抛出一个PermissionDenied异常，返回403 Forbidden错误。
        """
        obj = self.get_object()
        # 当简历不公开的时候，非所有者访问直接拒绝，公开的就不需要校验直接返回
        if obj.is_open is False and obj.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
