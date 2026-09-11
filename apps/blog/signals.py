# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.urls import reverse

from .models import Article, FriendLink, Tag, Category, MenuLink, Subject
from comment.models import SystemNotification, ArticleComment
from oauth.models import Ouser


def _clear_sidebar_cache(*keys):
    # 延迟导入，避免 app 加载期的循环依赖
    from .templatetags.blog_tags import clear_sidebar_cache
    clear_sidebar_cache(*keys)


@receiver([post_save, post_delete], sender=Article)
def article_change_clear_sidebar_cache(sender, instance, **kwargs):
    """
    文章增删改后清掉全部侧边栏统计缓存（文章数、标签计数、分类计数都会变）。

    仅浏览量变化时跳过：update_views 每次浏览都会 save(update_fields=['views'])，
    若也清缓存会导致缓存形同虚设。
    """
    update_fields = kwargs.get('update_fields')
    if update_fields and set(update_fields) <= {'views'}:
        return
    _clear_sidebar_cache()


# 各模型只失效真正受影响的缓存，避免评论这类高频写入把标签/分类缓存也一起冲掉。
# key 取自 blog_tags 的常量（延迟构建），避免两处硬编码漂移。
_SIDEBAR_KEYS_BY_SENDER = None


def _get_sidebar_keys_by_sender():
    global _SIDEBAR_KEYS_BY_SENDER
    if _SIDEBAR_KEYS_BY_SENDER is None:
        from .templatetags.blog_tags import (
            BLOG_INFO_CACHE_KEY, TAG_LIST_CACHE_KEY,
            CATEGORY_LIST_CACHE_KEY, MENU_LINK_CACHE_KEY,
        )
        _SIDEBAR_KEYS_BY_SENDER = {
            'Tag': (TAG_LIST_CACHE_KEY, BLOG_INFO_CACHE_KEY),
            'Category': (CATEGORY_LIST_CACHE_KEY,),
            'MenuLink': (MENU_LINK_CACHE_KEY,),
            'ArticleComment': (BLOG_INFO_CACHE_KEY,),
            # 专题增删会改变侧边栏的「专题」总数
            'Subject': (BLOG_INFO_CACHE_KEY,),
        }
    return _SIDEBAR_KEYS_BY_SENDER


@receiver([post_save, post_delete], sender=Tag)
@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=MenuLink)
@receiver([post_save, post_delete], sender=ArticleComment)
@receiver([post_save, post_delete], sender=Subject)
def related_change_clear_sidebar_cache(sender, instance, **kwargs):
    """标签/分类/菜单/评论/专题变化后，只清掉真正受影响的侧边栏缓存。

    映射漏配时退回「清全部」：只会多清一点缓存，不会因 KeyError 打断用户的保存请求。
    """
    from .templatetags.blog_tags import SIDEBAR_CACHE_KEYS
    mapping = _get_sidebar_keys_by_sender()
    _clear_sidebar_cache(*mapping.get(sender.__name__, SIDEBAR_CACHE_KEYS))


@receiver(post_save, sender=FriendLink)
def friend_link_create_signal(sender, instance, created, **kwargs):
    """
    创建新的友情链接则自带给管理员推送审核消息
    @param sender:
    @param instance:
    @param created:
    @param kwargs:
    @return:
    """
    # 判断是否是第一次生成
    if created:
        superuser = Ouser.objects.filter(is_superuser=True)
        title = f'增加一个新的{instance._meta.verbose_name}:{instance.name}'
        admin_url = reverse('admin:blog_friendlink_change', args=[instance.id])
        content = f'<p><a href="{admin_url}">友链地址：{instance.link}，' \
                  f'描述：{instance.description}，待管理员审核！！！</a></p>'
        new_notify = SystemNotification(title=title, content=content)
        new_notify.save()  # 保存实例

        # 在保存实例后，将关联对象添加到多对多关系中
        new_notify.get_p.set(superuser)


@receiver(post_save, sender=Article)
def article_create_signal(sender, instance, created, **kwargs):
    """
    创建新文章且状态为未发布时，给管理员推送通知
    @param sender:
    @param instance:
    @param created:
    @param kwargs:
    @return:
    """
    if created and not instance.is_publish:
        superuser = Ouser.objects.filter(is_superuser=True)
        title = f'新草稿文章：{instance.title}'
        article_url = instance.get_absolute_url()
        content = f'<p><a href="{article_url}">文章《{instance.title}》已创建为草稿，' \
                  f'待管理员审核发布。</a></p>'
        new_notify = SystemNotification(title=title, content=content)
        new_notify.save()

        # 在保存实例后，将关联对象添加到多对多关系中
        new_notify.get_p.set(superuser)
