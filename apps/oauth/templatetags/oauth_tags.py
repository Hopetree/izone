# 创建了新的tags标签文件后必须重启服务器

from django import template

register = template.Library()

# 用户相关标签函数
@register.simple_tag
def get_show_name(user):
    '''返回用户的展示名，优先选择昵称'''
    if user.nickname:
        return user.nickname
    return user.username

@register.inclusion_tag('oauth/tags/user_avatar.html')
def get_user_avatar_tag(user):
    '''返回用户的头像，是一个img标签'''
    return {'user':user}

@register.filter
def get_email_secret(email):
    '''返回邮箱的省略形式'''
    e_right = email.split('@')[-1]
    e_left = email.split('@')[0]
    return e_left[:2] + '...' + '@' + e_right