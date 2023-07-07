# 创建了新的tags标签文件后必须重启服务器
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from django import template
from ..models import (
    Article,
    Category,
    Tag,
    Carousel,
    FriendLink,
    Timeline
)
from django.db.models.aggregates import Count
from django.utils.html import mark_safe
import re

register = template.Library()


# 文章相关标签函数
@register.simple_tag
def get_article_list(sort=None, num=None):
    """获取指定排序方式和指定数量的文章"""
    if sort:
        if num:
            return Article.objects.filter(is_publish=True).order_by(sort)[:num]
        return Article.objects.filter(is_publish=True).order_by(sort)
    if num:
        return Article.objects.filter(is_publish=True)[:num]
    return Article.objects.filter(is_publish=True)


@register.simple_tag
def keywords_to_str(art):
    """将文章关键词变成字符串"""
    keys = art.keywords.all()
    return ','.join([key.name for key in keys])


@register.simple_tag
def get_tag_list():
    """返回标签列表"""
    return Tag.objects.filter(article__is_publish=True).annotate(
        total_num=Count('article')).filter(total_num__gt=0)


@register.simple_tag
def get_category_list():
    """返回分类列表"""
    return Category.objects.filter(article__is_publish=True).annotate(
        total_num=Count('article')).filter(total_num__gt=0)


@register.inclusion_tag('blog/tags/article_list.html')
def load_article_summary(articles, user):
    """返回文章列表模板"""
    return {'articles': articles, 'user': user}


@register.inclusion_tag('blog/tags/pagecut.html', takes_context=True)
def load_pages(context):
    """分页标签模板，不需要传递参数，直接继承参数"""
    return context


# 其他函数
@register.simple_tag
def get_carousel_list():
    """获取轮播图片列表"""
    return Carousel.objects.all()


@register.simple_tag
def get_new_timeline_id():
    """得到最后一个timeline的id，用来设置到缓存里面，实现动态缓存"""
    return Timeline.objects.order_by('-pk').first().pk


@register.simple_tag
def get_new_article_id():
    """得到最后一个article的id，用来设置到缓存里面，实现动态缓存"""
    return Article.objects.order_by('-pk').first().pk


@register.simple_tag
def get_star(num):
    """得到一排星星"""
    tag_i = '<i class="fa fa-star"></i>'
    return mark_safe(tag_i * num)


@register.simple_tag
def get_star_title(num):
    """得到星星个数的说明"""
    the_dict = {
        1: '【1颗星】：微更新，涉及轻微调整或者后期规划了内容',
        2: '【2颗星】：小更新，小幅度调整，一般不会迁移表格',
        3: '【3颗星】：中等更新，一般会增加或减少模块，有表格的迁移',
        4: '【4颗星】：大更新，涉及到应用的增减',
        5: '【5颗星】：最大程度更新，一般涉及多个应用和表格的变动',
    }
    return the_dict[num]


@register.simple_tag
def my_highlight(text, q):
    """自定义标题搜索词高亮函数，忽略大小写"""
    if len(q) > 1:
        try:
            text = re.sub(q, lambda a: '<span class="highlighted">{}</span>'.format(a.group()),
                          text, flags=re.IGNORECASE)
            text = mark_safe(text)
        except:
            pass
    return text


@register.simple_tag
def get_request_param(request, param, default=None):
    """获取请求的参数"""
    return request.POST.get(param) or request.GET.get(param, default)


@register.simple_tag
def get_friends(is_show=True, is_active=True):
    """获取友情链接"""
    return FriendLink.objects.filter(is_show=is_show, is_active=is_active)


@register.simple_tag
def now_hour():
    """返回当前时间的小时数"""
    return datetime.now().hour


@register.simple_tag
def deal_with_full_path(full_path, key, value):
    """
    处理当前路径，包含参数的
    @param value: 参数值
    @param key: 要修改的参数，也可以新增
    @param full_path: /search/?q=python&page=2
    @return: 得到新的路径
    """
    parsed_url = urlparse(full_path)
    query_params = parse_qs(parsed_url.query)
    # 去除参数key
    query_params[key] = value
    # 重新生成URL
    updated_query_string = urlencode(query_params, doseq=True)
    updated_url = urlunparse(parsed_url._replace(query=updated_query_string))
    return updated_url
