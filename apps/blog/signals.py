# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.urls import reverse

from .models import Article, FriendLink, Tag, Category, MenuLink
from comment.models import SystemNotification, ArticleComment
from oauth.models import Ouser


def _clear_sidebar_cache():
    # 延迟导入，避免 app 加载期的循环依赖
    from .templatetags.blog_tags import clear_sidebar_cache
    clear_sidebar_cache()


@receiver([post_save, post_delete], sender=Article)
def article_change_clear_sidebar_cache(sender, instance, **kwargs):
    """
    文章增删改后清掉侧边栏统计缓存。

    仅浏览量变化时跳过：update_views 每次浏览都会 save(update_fields=['views'])，
    若也清缓存会导致缓存形同虚设。
    """
    update_fields = kwargs.get('update_fields')
    if update_fields and set(update_fields) <= {'views'}:
        return
    _clear_sidebar_cache()


@receiver([post_save, post_delete], sender=Tag)
@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=MenuLink)
@receiver([post_save, post_delete], sender=ArticleComment)
def related_change_clear_sidebar_cache(sender, instance, **kwargs):
    """标签/分类/菜单/评论变化后清掉侧边栏统计缓存"""
    _clear_sidebar_cache()


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
