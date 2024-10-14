# -*- coding: utf-8 -*-
import time

from celery import shared_task
from django.core.management import call_command

from .utils import TaskResponse
from .actions import (
    action_update_article_cache,
    # action_check_friend_links,
    action_clear_notification,
    action_cleanup_task_result,
    action_baidu_push,
    action_check_site_links,
    action_publish_article_by_task,
    action_write_or_update_view,
    action_get_feed_data
)
from monitor.actions import (
    action_check_host_status
)

from blog.templatetags.blog_tags import get_blog_infos

from .action.oss_sync import action_qiniu_sync_github
from .action.article_sync import action_article_to_github
from .action.friend_links import action_check_friend_links
from .action.clear_redis_keys import action_clear_cache_with_prefix


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
def baidu_push(baidu_url, weeks=1):
    """
    百度推送
    @param baidu_url:
    @param weeks:
    @return:
    """
    response = TaskResponse()
    result = action_baidu_push(baidu_url=baidu_url, weeks=weeks)
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
def publish_article_by_task(article_ids, filter_rule=None):
    """
    定时将草稿发布出去
    @param article_ids: 需要发布的文章ID
    @param filter_rule: 发布规则，比如 {140:"0910"} 表示 id为140的文章只有在09月10日之后才发布
    @return:
    """
    response = TaskResponse()
    result = action_publish_article_by_task(article_ids, filter_rule=filter_rule)
    response.data = result
    return response.as_dict()


@shared_task
def set_views_to_redis():
    """
    定时读取每日的文章访问量，写入redis，一定要设置一个23:59分执行的任务
    @return:
    """
    response = TaskResponse()
    # 先将统计数据写入模型，然后分析后写入redis
    action_write_or_update_view()
    response.data = {'msg': 'write ok'}
    return response.as_dict()


@shared_task
def set_feed_data():
    """
    定时采集feed数据，回写到数据库
    """
    response = TaskResponse()
    # 先将统计数据写入模型，然后分析后写入redis
    response.data = action_get_feed_data()
    return response.as_dict()


@shared_task
def clear_expired_sessions():
    """
    定时清理过期的session
    @return:
    """
    response = TaskResponse()
    call_command('clearsessions')
    response.data = {'msg': 'clear sessions done'}
    return response.as_dict()


@shared_task
def check_host_status(recipient_list=None, times=None, ignore_hours=None):
    """
    定时检查服务监控的节点状态
    定时任务需要设置1分钟执行一次
    @param ignore_hours: 忽略时段，在这些时段不检查状态
    @param times: 通知频率，默认[1, 10, 60, 60 * 4, 60 * 24]
    @param recipient_list: 收件人的邮件地址，必填，否则不检查
    @return:
    """
    response = TaskResponse()
    msg = action_check_host_status(recipient_list=recipient_list, times=times,
                                   ignore_hours=ignore_hours)
    response.data = {'msg': msg}
    return response.as_dict()


# name: 指定任务的名称。
# max_retries: 设置任务的最大重试次数
# default_retry_delay: 设置任务重试的默认延迟时间（单位为秒）
# retry_kwargs: 允许为重试指定额外的关键字参数
@shared_task(max_retries=2, default_retry_delay=10)
def qiniu_sync_github(access_key, secret_key, bucket_name, private_domain,
                      token, owner, repo, max_num=10, msg=None):
    """
    七牛云空间同步到GitHub，空间到项目
    @param access_key: 七牛密钥
    @param secret_key: 七牛密钥
    @param bucket_name: 七牛空间名，如blog-img
    @param private_domain: 七牛空间私有域名，如pic.tendcode.com
    @param token: GitHub token
    @param owner: GitHub 用户名，如Hopetree
    @param repo: GitHub 项目名，如img
    @param max_num: 每次同步的数量，如果要一次同步所以则设置大一点就行
    @param msg: GitHub 上传文件时候的 commit 信息，不填则按照默认信息
    @return:
    """
    response = TaskResponse()
    result = action_qiniu_sync_github(
        access_key, secret_key, bucket_name, private_domain,
        token, owner, repo, max_num, msg
    )
    response.data = result
    return response.as_dict()


@shared_task(max_retries=2, default_retry_delay=30)
def article_to_github(base_url, base64_string, token, owner, repo,
                      source_media_url, target_media_url,
                      msg='Sync from blog task',
                      full=False, white_list=None, prefix='blog'):
    """
    同步文章到GitHub
    @param base_url: 博客接口地址，如https://tendcode.com
    @param base64_string: 管理员用户密码base64值
    @param token: GitHub token
    @param owner: GitHub 用户名，如Hopetree
    @param repo: GitHub 项目名，如img
    @param source_media_url: 媒体文件源地址前缀，如https://tendcode.com/cdn/
    @param target_media_url: 媒体文件替换后地址前缀，如https://cdn.jsdelivr.net/gh/Hopetree/blog-img@main/
    @param msg: GitHub 提交信息，如Upload file via API
    @param full: 是否全量同步，布尔值，默认False
    @param white_list: 白名单，list，文章的slug
    @param prefix: GitHub中文章保存路径，如blog
    @return:
    """
    response = TaskResponse()
    result = action_article_to_github(
        base_url, base64_string, token, owner, repo,
        source_media_url, target_media_url,
        msg, full, white_list, prefix
    )
    response.data = result
    return response.as_dict()


@shared_task
def clear_cache_with_prefix(pattern_keys):
    """
    清理指定匹配规则的redis keys
    @param pattern_keys: health.*
    @return:
    """
    response = TaskResponse()
    result = action_clear_cache_with_prefix(pattern_keys)
    response.data = result
    return response.as_dict()
