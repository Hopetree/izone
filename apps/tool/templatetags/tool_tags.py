# -*- coding: utf-8 -*-
from django import template
from django.db.models.aggregates import Count
from ..models import ToolCategory,ToolLink

register = template.Library()

@register.simple_tag
def get_toolcates():
    '''获取所有工具分类，只显示有工具的分类'''
    return ToolCategory.objects.annotate(total_num=Count('toollink')).filter(total_num__gt=0)

@register.simple_tag
def get_toollinks(cate):
    '''获取单个分类下所有工具'''
    return cate.toollink_set.all()
