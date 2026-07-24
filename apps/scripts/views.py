import re
import markdown
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views import generic

from .models import Script


def make_markdown():
    """轻量 markdown 渲染，只含基础扩展和代码高亮"""
    from blog.views import CustomHtmlFormatter
    from markdown.extensions.codehilite import CodeHiliteExtension
    from markdown.extensions.toc import TocExtension
    from utils.markdown_ext import (
        DelExtension, IconExtension, AlertExtension,
        CodeItemExtension, CodeGroupExtension
    )
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        CodeHiliteExtension(pygments_formatter=CustomHtmlFormatter),
        TocExtension(slugify=slugify),
        DelExtension(),
        IconExtension(),
        AlertExtension(),
        CodeItemExtension(),
        CodeGroupExtension()
    ])
    return md


def preprocess_mermaid_blocks(md_content):
    """预处理 mermaid 代码块"""
    mermaid_pattern = re.compile(
        r'^\s*```mermaid\s*\n(.*?)\n```', re.DOTALL | re.MULTILINE
    )
    has_mermaid = False

    def replace_mermaid_block(match):
        nonlocal has_mermaid
        content = match.group(1).strip()
        if content:
            has_mermaid = True
            return f"<pre class='mermaid'>\n{content}\n</pre>"
        return match.group(0)

    processed = mermaid_pattern.sub(replace_mermaid_block, md_content)
    return processed, has_mermaid


class AdminRequiredMixin:
    """要求管理员权限"""
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ScriptListView(AdminRequiredMixin, generic.ListView):
    model = Script
    template_name = 'scripts/list.html'
    context_object_name = 'scripts'
    paginate_by = getattr(settings, 'BASE_PAGE_BY', 10)
    paginate_orphans = getattr(settings, 'BASE_ORPHANS', 3)

    def get_queryset(self):
        qs = Script.objects.all()
        script_type = self.request.GET.get('type')
        if script_type in ('shell', 'python'):
            qs = qs.filter(script_type=script_type)
        return qs.order_by('-create_date')


class ScriptDetailView(AdminRequiredMixin, generic.DetailView):
    model = Script
    template_name = 'scripts/detail.html'
    context_object_name = 'script'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_publish and not self.request.user.is_superuser:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        script = self.object

        # 渲染 markdown 说明文档（内容少，每次直接渲染）
        md_content, has_mermaid = preprocess_mermaid_blocks(script.description)
        md = make_markdown()
        context['body'] = md.convert(md_content)
        context['has_mermaid'] = has_mermaid

        # 用 markdown 渲染代码块，获得和文章一致的 codehilite + code-wrapper 结构
        lang = 'bash' if script.script_type == 'shell' else 'python'
        code_md = f'```{lang}\n{script.code}\n```'
        context['highlighted_code'] = md.convert(code_md)

        return context


def script_raw(request, slug):
    """公开端点，返回纯文本脚本代码供 curl 下载，仅已发布脚本可访问"""
    script = get_object_or_404(Script, slug=slug, is_publish=True)
    content_type = {
        'shell': 'text/x-sh',
        'python': 'text/x-python',
    }.get(script.script_type, 'text/plain')
    response = HttpResponse(script.code, content_type=f'{content_type}; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{script.filename}"'
    return response


@staff_member_required
@require_POST
def publish_script(request):
    """发布脚本，仅管理员可操作"""
    script_slug = request.POST.get('slug')
    try:
        script = Script.objects.get(slug=script_slug)
        if script.is_publish:
            return JsonResponse({'message': '脚本已是发布状态', 'code': 1})
        script.is_publish = True
        script.save()
        return JsonResponse({'message': '发布成功', 'code': 0})
    except Script.DoesNotExist:
        return JsonResponse({'message': '脚本不存在', 'code': 1}, status=404)
