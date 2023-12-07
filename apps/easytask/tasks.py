# -*- coding: utf-8 -*-
import time

from celery import shared_task

from .utils import TaskResponse
from .actions import (
    action_update_article_cache,
    action_check_friend_links,
    action_clear_notification,
    action_cleanup_task_result,
    action_baidu_push,
    action_check_site_links,
    action_publish_article_by_task,
    ArticleViewsTool,
)

from blog.templatetags.blog_tags import get_blog_infos


@shared_task
def simple_task(x, y):
    time.sleep(2)
    return x + y


@shared_task
def update_cache():
    """
    更新各种缓存
    @return:
    """
    response = TaskResponse()
    article_result = action_update_article_cache()
    response.data['article'] = article_result
    # 博客统计信息
    blog_info_result = get_blog_infos()
    response.data['blog_infos'] = blog_info_result
    return response.as_dict()


@shared_task
def check_friend(site_link=None, white_list=None):
    """
    检查友链
    @return:
    """
    response = TaskResponse()
    check_result = action_check_friend_links(site_link=site_link, white_list=white_list)
    response.data = check_result
    return response.as_dict()


@shared_task
def clear_notification(day=200, is_read=True):
    """
    清理过期通知信息
    @param is_read:
    @param day:
    @return:
    """
    response = TaskResponse()
    result = action_clear_notification(day=day, is_read=is_read)
    response.data = result
    return response.as_dict()


@shared_task
def cleanup_task_result(day=3):
    """
    清理任务结果
    清理day天前成功或结束的，其他状态的一概不清理
    @param day:
    @return:
    """
    response = TaskResponse()
    result = action_cleanup_task_result(day=day)
    response.data = result
    return response.as_dict()


@shared_task
def baidu_push(baidu_url, months=3):
    """
    百度推送
    @param baidu_url:
    @param months:
    @return:
    """
    response = TaskResponse()
    result = action_baidu_push(baidu_url=baidu_url, months=months)
    response.data = result
    return response.as_dict()


@shared_task
def check_navigation_site(white_domain_list=None):
    """
    校验导航网站有效性，只校验状态为True或者False的，为空的不校验，所以特殊地址可以设置成空跳过校验
    @param white_domain_list: 网站名称白名单，忽略校验
    @return:
    """
    response = TaskResponse()
    result = action_check_site_links(white_domain_list)
    response.data = result
    return response.as_dict()


@shared_task
def publish_article_by_task(article_ids):
    """
    定时将草稿发布出去
    @param article_ids: 需要发布的文章ID
    @return:
    """
    response = TaskResponse()
    result = action_publish_article_by_task(article_ids)
    response.data = result
    return response.as_dict()


@shared_task
def set_views_to_redis():
    """
    定时读取每日的文章访问量，写入redis，一定要设置一个23:59分执行的任务
    @return:
    """
    response = TaskResponse()
    result = ArticleViewsTool().set_data_to_redis()
    response.data = result
    return response.as_dict()
