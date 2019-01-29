# 创建了新的tags标签文件后必须重启服务器

from django import template

register = template.Library()

@register.inclusion_tag('oauth/tags/user_avatar.html')
def get_user_avatar_tag(user):
    '''返回用户的头像，是一个img标签'''
    return {'user':user}


@register.simple_tag
def http_to_https(link):
    '''将http链接替换成https，目的是将微博的头像图床地址换成HTTPS'''
    return link.replace('http://','https://')