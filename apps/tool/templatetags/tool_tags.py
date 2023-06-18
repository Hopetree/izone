# -*- coding: utf-8 -*-
from django import template
from django.db.models.aggregates import Count
from django.templatetags.static import static
from django.urls import reverse

from ..models import ToolCategory
from ..utils import IZONE_TOOLS

register = template.Library()


@register.simple_tag
def get_toolcates():
    """获取所有工具分类，只显示有工具的分类"""
    return ToolCategory.objects.annotate(total_num=Count('toollink')).filter(
        total_num__gt=0)


@register.simple_tag
def get_toollinks(cate):
    """获取单个分类下所有工具"""
    return cate.toollink_set.all()


@register.simple_tag
def get_toollist_by_key(key=None):
    """返回工具列表"""
    tools = []
    if not key or key not in IZONE_TOOLS:
        for _k in IZONE_TOOLS:
            _tag = IZONE_TOOLS[_k]['tag']
            _tools = IZONE_TOOLS[_k]['tools']
            for each in _tools:
                item = {'tag': _tag,
                        'name': each['name'],
                        'url': reverse(each['url']),
                        'img': static(each['img']),
                        'desc': each['desc']}
                tools.append(item)
    else:
        _tag = IZONE_TOOLS[key]['tag']
        _tools = IZONE_TOOLS[key]['tools']
        for each in _tools:
            item = {'tag': _tag,
                    'name': each['name'],
                    'url': reverse(each['url']),
                    'img': static(each['img']),
                    'desc': each['desc']}
            tools.append(item)
    return tools


@register.inclusion_tag('tool/tags/tool_item.html')
def load_tool_item(item):
    """返回单个工具显示栏"""
    return {'tool_item': item}


@register.inclusion_tag('tool/tags/github_corners.html')
def load_github_corners(position, color, url):
    """
    加载github项目跳转，根据颜色返回
    """
    return {'position': position, 'color': color, 'url': url}
