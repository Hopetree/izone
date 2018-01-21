# 创建了新的tags标签文件后必须重启服务器

from django import template

register = template.Library()

@register.simple_tag
def get_comment_count(entry):
    '''获取一个文章的评论总数'''
    lis = entry.article_comments.all()
    return lis.count()

@register.simple_tag
def get_parent_comments(entry):
    '''获取一个文章的父评论列表'''
    lis = entry.article_comments.filter(parent=None)
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
def get_notifications(user,f=None):
    '''获取一个用户的对应条件下的提示信息'''
    if f=='true':
        lis = user.notification_get.filter(is_read=True)
    elif f=='false':
        lis = user.notification_get.filter(is_read=False)
    else:
        lis = user.notification_get.all()
    return lis

@register.simple_tag
def get_notifications_count(user,f=None):
    '''获取一个用户的对应条件下的提示信息总数'''
    if f=='true':
        lis = user.notification_get.filter(is_read=True)
    elif f=='false':
        lis = user.notification_get.filter(is_read=False)
    else:
        lis = user.notification_get.all()
    return lis.count()