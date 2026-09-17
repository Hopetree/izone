from django import template
from django.core.cache import cache
from django.db.models import Prefetch
from ..models import emoji_info, ArticleComment

# 未读通知计数的缓存时间（秒）：导航栏每页都会用到，短缓存即可
NOTIFICATION_COUNT_CACHE_TTL = 60

# 创建了新的tags标签文件后必须重启服务器
register = template.Library()


@register.simple_tag
def get_comment_count(entry):
    """获取一个文章的评论总数。

    列表页视图已注解 comment_num，优先复用避免每篇文章再查一次；其他调用方没有注解时回退到 COUNT。
    """
    num = getattr(entry, 'comment_num', None)
    if num is not None:
        return num
    return entry.article_comments.count()


@register.simple_tag
def get_parent_comments(entry):
    """获取一个文章的父评论列表，逆序只选取后面的20个评论。

    一次性预取作者、被回复人、头像/认证所需的社会化账号与邮箱，以及每个父评论的子评论，
    避免模板里逐条评论回库（原来每条评论会额外触发多次查询）。
    """
    cached = getattr(entry, '_parent_comments', None)
    if cached is not None:
        return cached

    children = Prefetch(
        'articlecomment_child_comments',
        queryset=ArticleComment.objects
        .select_related('author', 'rep_to__author')
        .prefetch_related('author__socialaccount_set', 'author__emailaddress_set'),
        to_attr='prefetched_children',
    )
    lis = (entry.article_comments
           .filter(parent=None)
           .select_related('author', 'rep_to__author')
           .prefetch_related('author__socialaccount_set', 'author__emailaddress_set', children)
           .order_by('-id')[:20])
    entry._parent_comments = lis
    return lis


@register.simple_tag
def get_child_comments(com):
    """获取一个父评论的子评论列表；父评论已在 get_parent_comments 中预取过就直接复用"""
    prefetched = getattr(com, 'prefetched_children', None)
    if prefetched is not None:
        return prefetched
    return com.articlecomment_child_comments.all()


@register.simple_tag
def get_comment_user_count(entry):
    """获取评论人总数（一条去重计数查询，替代原来把全部评论取回内存去重）"""
    return entry.article_comments.values('author').distinct().count()


@register.simple_tag
def _notification_count_cache_key(user_id, f):
    return f'comment:notif_count:{user_id}:{f or "all"}'


def clear_notification_count_cache(user_id):
    """通知增删或已读状态变化时清掉计数缓存"""
    cache.delete_many([_notification_count_cache_key(user_id, f)
                       for f in ('true', 'false', None)])


def clear_all_notification_count_cache():
    """清掉所有用户的计数缓存（系统通知是群发，定位不到单个用户）"""
    delete_pattern = getattr(cache, 'delete_pattern', None)
    if delete_pattern is not None:
        delete_pattern('comment:notif_count:*')
    # 若缓存后端不支持按模式删除，则依赖 60 秒 TTL 自然过期


@register.simple_tag
def get_notifications(user, f=None):
    """获取一个用户的对应条件下的提示信息（最多 50 条）。

    两侧各取最近 50 条再合并排序，避免把所有通知都读进内存；
    预取评论所属文章与创建者，避免模板逐条回库（模板会用到 each.comment.belong.*）。
    """
    limit = 50
    if f == 'true':
        q1 = user.notification_get.filter(is_read=True)
        q2 = user.systemnotification_recipient.filter(is_read=True)
    elif f == 'false':
        q1 = user.notification_get.filter(is_read=False)
        q2 = user.systemnotification_recipient.filter(is_read=False)
    else:
        q1 = user.notification_get.all()
        q2 = user.systemnotification_recipient.all()

    lis = list(q1.select_related('create_p', 'comment__belong').order_by('-create_date')[:limit])
    lis += list(q2.order_by('-create_date')[:limit])
    # 按照 create_date 字段进行汇总后重新排序
    lis.sort(key=lambda x: x.create_date, reverse=True)
    return lis[:limit]


@register.simple_tag
def get_notifications_count(user, f=None):
    """获取一个用户的对应条件下的提示信息总数。

    这个标签在导航栏和 base.html 里每页都会调用，直接查询就是每页 2 次 COUNT，
    因此加 60 秒缓存；标记已读/删除时会立即清缓存（见 comment/signals.py）。
    """
    if not user.is_authenticated:
        return 0
    cache_key = _notification_count_cache_key(user.id, f)
    num = cache.get(cache_key)
    if num is not None:
        return num
    if f == 'true':
        num = (user.notification_get.filter(is_read=True).count()
               + user.systemnotification_recipient.filter(is_read=True).count())
    elif f == 'false':
        num = (user.notification_get.filter(is_read=False).count()
               + user.systemnotification_recipient.filter(is_read=False).count())
    else:
        num = user.notification_get.count() + user.systemnotification_recipient.count()
    cache.set(cache_key, num, NOTIFICATION_COUNT_CACHE_TTL)
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
                if k in system_info.strip():
                    system_img = v
                    break
        if browser_img == 'other_browser':
            for k, v in browser_dict.items():
                if k in browser_info.strip():
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