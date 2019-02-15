# 创建了新的tags标签文件后必须重启服务器

from django import template
from ..models import emoji_info

register = template.Library()


@register.simple_tag
def get_comment_count(entry):
    '''获取一个文章的评论总数'''
    lis = entry.article_comments.all()
    return lis.count()


@register.simple_tag
def get_parent_comments(entry):
    '''获取一个文章的父评论列表，逆序只选取后面的20个评论'''
    lis = entry.article_comments.filter(parent=None).order_by("-id")[:20]
    return lis


@register.simple_tag
def get_child_comments(com):
    '''获取一个父评论的子平路列表'''
    lis = com.articlecomment_child_comments.all()
    return lis


@register.simple_tag
def get_comment_user_count(entry):
    '''获取评论人总数'''
    p = []
    lis = entry.article_comments.all()
    for each in lis:
        if each.author not in p:
            p.append(each.author)
    return len(p)


@register.simple_tag
def get_notifications(user, f=None):
    '''获取一个用户的对应条件下的提示信息'''
    if f == 'true':
        lis = user.notification_get.filter(is_read=True)
    elif f == 'false':
        lis = user.notification_get.filter(is_read=False)
    else:
        lis = user.notification_get.all()
    return lis


@register.simple_tag
def get_notifications_count(user, f=None):
    '''获取一个用户的对应条件下的提示信息总数'''
    if f == 'true':
        lis = user.notification_get.filter(is_read=True)
    elif f == 'false':
        lis = user.notification_get.filter(is_read=False)
    else:
        lis = user.notification_get.all()
    return lis.count()


@register.simple_tag
def get_emoji_imgs():
    '''
    返回一个列表，包含表情信息
    :return:
    '''
    return emoji_info


@register.filter(is_safe=True)
def emoji_to_url(value):
    """
    将emoji表情的名称转换成图片地址
    """
    emoji_static_url = 'comment/weibo/{}.png'
    return emoji_static_url.format(value)
