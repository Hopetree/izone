# 创建了新的tags标签文件后必须重启服务器

from django import template

register = template.Library()


@register.inclusion_tag('oauth/tags/user_avatar.html')
def get_user_avatar_tag(user):
    '''返回用户的头像，是一个img标签'''
    return {'user': user}


@register.simple_tag
def http_to_https(link):
    '''将http链接替换成https，目的是将微博的头像图床地址换成HTTPS'''
    return link.replace('http://', 'https://')


@register.simple_tag
def get_user_link(user):
    '''
    获取认证用户的link，并判断用户是哪种认证方式（Github，Weibo，邮箱）
    参考 get_social_accounts(user) 的用法
    :param user: 一个USER对象
    :return: 返回用户的link和注册方式以及是否验证过邮箱地址,link的优先顺序是user.link，其次是github主页，
            考虑到很多人不愿意展示微博主页，所以不展示weibo主页
    '''
    info = {
        'link': None,
        'provider': None,
        'is_verified': False
    }
    accounts = {}
    for account in user.socialaccount_set.all().iterator():
        providers = accounts.setdefault(account.provider, [])
        providers.append(account)
    if accounts:
        for key in ['github', 'weibo']:
            account_users = accounts.get(key)
            if account_users:
                account_user = account_users[0]
                the_link = account_user.get_profile_url()
                the_provider = account_user.get_provider().name
                if key == 'github':
                    info['link'] = the_link
                if user.link:
                    info['link'] = user.link
                info['provider'] = the_provider
                info['is_verified'] = True
    else:
        the_link = user.link
        if the_link:
            info['link'] = the_link
        for emailaddress in user.emailaddress_set.all().iterator():
            if emailaddress.verified:
                info['is_verified'] = True
    return info
