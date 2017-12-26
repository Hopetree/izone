# 创建了新的tags标签文件后必须重启服务器

from django import template
from ..models import Article, Category, Tag, Timeline, Carousel, Keyword
from django.db.models.aggregates import Count
from django.utils.html import mark_safe

register = template.Library()

# 用户相关标签函数
@register.simple_tag
def get_show_name(user):
    '''返回用户的展示名，优先选择昵称'''
    if user.nickname:
        return user.nickname
    return user.username

# 文章相关标签函数
@register.simple_tag
def get_article_list(sort=None,num=None):
    '''获取所有文章'''
    if sort == '-views':
        if num:
            return Article.objects.order_by('-views', '-update_date')[:num]
        return Article.objects.order_by('-views', '-update_date')
    if num:
        return Article.objects.all()[:num]
    return Article.objects.all()



@register.simple_tag
def keywords_to_str(art):
    '''将文章关键词变成字符串'''
    keys = art.keywords.all()
    return ','.join([key.name for key in keys])

@register.simple_tag
def get_tag_list():
    '''返回标签列表'''
    return Tag.objects.annotate(total_num=Count('article')).filter(total_num__gt=0)

@register.simple_tag
def get_category_list():
    '''返回分类列表'''
    return Category.objects.annotate(total_num=Count('article')).filter(total_num__gt=0)

@register.inclusion_tag('blog/tags/article-list.html')
def load_article_summary(articles):
    '''返回文章列表模板'''
    return {'articles':articles}

@register.inclusion_tag('blog/tags/pagecut.html',takes_context=True)
def load_pages(context):
    '''分页标签模板，不需要传递参数，直接继承参数'''
    return context

# 其他函数
@register.simple_tag
def get_carousel_list():
    '''获取轮播图片列表'''
    return Carousel.objects.all()