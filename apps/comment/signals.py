# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import ArticleComment, Notification, SystemNotification


def _clear_notification_count_cache(user_id):
    # 延迟导入，避免 app 加载期的循环依赖
    from .templatetags.comment_tags import clear_notification_count_cache
    clear_notification_count_cache(user_id)


def _clear_all_notification_count_cache():
    from .templatetags.comment_tags import clear_all_notification_count_cache
    clear_all_notification_count_cache()


@receiver([post_save, post_delete], sender=Notification)
def notification_change_clear_count(sender, instance, **kwargs):
    """通知新增/标记已读/删除后清掉该用户的未读计数缓存，让角标立即更新"""
    _clear_notification_count_cache(instance.get_p_id)


@receiver([post_save, post_delete], sender=SystemNotification)
def system_notification_change_clear_count(sender, instance, **kwargs):
    """系统通知是群发（get_p 是 M2M），无法定位单个用户，直接清掉所有计数缓存"""
    _clear_all_notification_count_cache()


@receiver(post_save, sender=ArticleComment)
def notify_handler(sender, instance, created, **kwargs):
    the_article = instance.belong
    create_p = instance.author
    # 判断是否是第一次生成评论，后续修改评论不会再次激活信号
    if created:
        if instance.rep_to:
            '''如果评论是一个回复评论，则同时通知给文章作者和回复的评论人，如果2者相等，则只通知一次'''
            if the_article.author == instance.rep_to.author:
                get_p = instance.rep_to.author
                if create_p != get_p:
                    new_notify = Notification(create_p=create_p, get_p=get_p, comment=instance)
                    new_notify.save()
            else:
                get_p1 = the_article.author
                if create_p != get_p1:
                    new1 = Notification(create_p=create_p, get_p=get_p1, comment=instance)
                    new1.save()
                get_p2 = instance.rep_to.author
                if create_p != get_p2:
                    new2 = Notification(create_p=create_p, get_p=get_p2, comment=instance)
                    new2.save()
        else:
            '''如果评论是一个一级评论而不是回复其他评论并且不是作者自评，则直接通知给文章作者'''
            get_p = the_article.author
            if create_p != get_p:
                new_notify = Notification(create_p=create_p, get_p=get_p, comment=instance)
                new_notify.save()
