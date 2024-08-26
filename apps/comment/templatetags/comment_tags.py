from django import template
from ..models import emoji_info

# 创建了新的tags标签文件后必须重启服务器
register = template.Library()


@register.simple_tag
def get_comment_count(entry):
    """获取一个文章的评论总数"""
    lis = entry.article_comments.all()
    return lis.count()


@register.simple_tag
def get_parent_comments(entry):
    """获取一个文章的父评论列表，逆序只选取后面的20个评论"""
    lis = entry.article_comments.filter(parent=None).order_by("-id")[:20]
    return lis


@register.simple_tag
def get_child_comments(com):
    """获取一个父评论的子平路列表"""
    lis = com.articlecomment_child_comments.all()
    return lis


@register.simple_tag
def get_comment_user_count(entry):
    """获取评论人总数"""
    p = []
    lis = entry.article_comments.all()
    for each in lis:
        if each.author not in p:
            p.append(each.author)
    return len(p)


@register.simple_tag
def get_notifications(user, f=None):
    """获取一个用户的对应条件下的提示信息"""
    if f == 'true':
        # 获取所有已读通知
        lis = []
        lis.extend(user.notification_get.filter(is_read=True))
        lis.extend(user.systemnotification_recipient.filter(is_read=True))
    elif f == 'false':
        # 获取所有未读通知
        lis = []
        lis.extend(user.notification_get.filter(is_read=False))
        lis.extend(user.systemnotification_recipient.filter(is_read=False))
    else:
        # 获取所有通知
        lis = []
        lis.extend(user.notification_get.all())
        lis.extend(user.systemnotification_recipient.all())

    # 按照 create_date 字段进行汇总后重新排序
    lis = sorted(lis, key=lambda x: x.create_date, reverse=True)
    return lis[:50]


@register.simple_tag
def get_notifications_count(user, f=None):
    """获取一个用户的对应条件下的提示信息总数"""
    if f == 'true':
        num = 0
        num += user.notification_get.filter(is_read=True).count()
        num += user.systemnotification_recipient.filter(is_read=True).count()
    elif f == 'false':
        num = 0
        num += user.notification_get.filter(is_read=False).count()
        num += user.systemnotification_recipient.filter(is_read=False).count()
    else:
        num = 0
        num += user.notification_get.all().count()
        num += user.systemnotification_recipient.all().count()
    return num


@register.simple_tag
def get_emoji_imgs():
    """
    返回一个列表，包含表情信息
    :return:
    """
    return emoji_info


@register.filter(is_safe=True)
def emoji_to_url(value):
    """
    将emoji表情的名称转换成图片地址
    """
    emoji_static_url = 'comment/weibo/{}.png'
    return emoji_static_url.format(value)


@register.simple_tag
def split_user_agent(user_agent):
    """
    将评论中的浏览器信息解析成系统版本和浏览器版本
    @param user_agent: PC / Windows 7 / Chrome 55.0.2891
    @return: Windows 7,Chrome 55.0.2891,windows,chrome
    """
    system_dict = {
        'Windows': 'Windows',
        'Mac': 'Mac',
        'iOS': 'iOS',
        'Android': 'Android',
        'Ubuntu': 'Ubuntu',
        'Linux': 'Linux',
    }
    browser_dict = {
        'Chrome': 'Chrome',
        'Firefox': 'Firefox',
        'Safari': 'Safari',
        'Edge': 'Edge',
        'IE': 'IE',
        'Opera': 'Opera'
    }
    system_info, browser_info = 'Unknown', 'Unknown'
    system_img, browser_img = 'other_system', 'other_browser'
    if user_agent and len(user_agent.split(' / ')) == 3:
        _, system_info, browser_info = user_agent.split(' / ')
        # 优先使用关键字开头匹配
        for k, v in system_dict.items():
            if system_info.strip().startswith(k):
                system_img = v
                break
        for k, v in browser_dict.items():
            if browser_info.strip().startswith(k):
                browser_img = v
                break
        # 如果开头匹配不到，则使用包含来匹配，开头匹配是优先的
        if system_img == 'other_system':
            for k, v in system_dict.items():
                if system_info.strip() in k:
                    system_img = v
                    break
        if browser_img == 'other_browser':
            for k, v in browser_dict.items():
                if browser_info.strip() in k:
                    browser_img = v
                    break
    return {
        'system_info': system_info.strip(),
        'browser_info': browser_info.strip(),
        'system_img': system_img,
        'browser_img': browser_img
    }

@register.inclusion_tag('comment/tags/user_agent.html')
def load_user_agent_img(user_agent):
    """
    加载user_agent页面内容
    @param user_agent:
    @return:
    """
    return {'user_agent': user_agent}