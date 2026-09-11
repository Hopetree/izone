# -*- coding: utf-8 -*-
"""
    定义一些任务的执行操作，将具体的操作从tasks.py里面抽离出来
    每个任务需要饮用的模块放到函数里面引用，方便单独调试函数
"""
import json
from datetime import datetime, timedelta

import requests
from django.db.models import Sum

from blog.models import Article, ArticleView, PageView
from blog.views import make_markdown, preprocess_mermaid_blocks


def get_link_status(url):
    """
    请求地址，返回请求状态和内容
    @param url:
    @return:
    """
    try:
        resp = requests.get(url, timeout=5, verify=False)
    except Exception:
        return 500, '请求超时'
    return resp.status_code, resp.text


def white_list_check(lis, string):
    """
    校验一个字符串是否包含一个列表中任意一个元素
    @param lis:
    @param string:
    @return: bool
    """
    for each in lis:
        if each in string:
            return True
    return False


def action_update_article_cache():
    """
    预热文章 markdown 缓存，缓存格式跟文章视图保持一致。

    原来用 cache.keys('article:markdown:*') 扫全部 key，Redis 的 KEYS 会阻塞服务端；
    改为逐篇 cache.get 判断，并且只处理已发布文章、正文延迟加载（未命中的才取 body）。
    @return:
    """
    from django.core.cache import cache
    from blog.models import Article

    total_num, done_num = 0, 0
    # 只取 id/update_date，正文延迟到确实需要渲染时再取，避免把所有文章正文读进内存
    for obj in Article.objects.filter(is_publish=True).only('id', 'update_date'):
        total_num += 1
        ud = obj.update_date.strftime('%Y%m%d%H%M%S')
        md_key = f'article:markdown:{obj.id}:{ud}'
        if cache.get(md_key):
            continue
        md = make_markdown()
        processed_content, has_mermaid = preprocess_mermaid_blocks(obj.body)
        # 设置过期时间的时候分散时间，不要设置成同一时间
        cache.set(md_key, (md.convert(processed_content), md.toc, has_mermaid),
                  3600 * 24 * 7 + 10 * done_num)
        done_num += 1
    data = {'total': total_num, 'done': done_num}
    return data


def action_clear_notification(day=200, is_read=True):
    """
    清理消息推送
    @param is_read: False表示清理所有，True表示只清理已读，默认清理已读
    @param day: 清理day天前的信息
    @return:
    """
    from django.db.models import Q
    from comment.models import Notification, SystemNotification

    current_date = datetime.now()
    delta = timedelta(days=day)
    past_date = current_date - delta
    if is_read is True:
        query = Q(create_date__lte=past_date, is_read=True)
    else:
        query = Q(create_date__lte=past_date)

    comment_notification_objects = Notification.objects.filter(query)
    system_notification_objects = SystemNotification.objects.filter(query)
    comment_num = comment_notification_objects.count()
    system_num = system_notification_objects.count()
    comment_notification_objects.delete()
    system_notification_objects.delete()
    return {'comment_num': comment_num, 'system_num': system_num}


def action_cleanup_task_result(day=3):
    """
    清理任务结果
    清理day天前成功或结束的，其他状态的一概不清理
    @return:
    """
    from django.db.models import Q
    from django_celery_results.models import TaskResult

    current_date = datetime.now()
    delta = timedelta(days=day)
    past_date = current_date - delta
    query = Q(date_done__lte=past_date)
    task_result_objects = TaskResult.objects.filter(query)
    task_result_count = task_result_objects.count()
    task_result_objects.delete()
    return {'task_result_count': task_result_count}


def action_baidu_push(baidu_url, weeks):
    """
    主动推送文章地址到百度，指定推送最近months月的文章链接
    @param baidu_url: 百度接口调用地址，包含token
    @param weeks: 几周内的文章
    @return:
    """
    import requests
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    from blog.models import Article
    from blog.utils import site_full_url

    def baidu_push(urls):
        headers = {
            'User-Agent': 'curl/7.12.1',
            'Host': 'data.zz.baidu.com',
            'Content-Type': 'text/plain',
            'Content-Length': '83'
        }
        try:
            response = requests.post(baidu_url, headers=headers, data=urls, timeout=5)
            return True, response.json()
        except Exception as e:
            return False, e

    current_date = datetime.now()
    previous_date = current_date - relativedelta(weeks=weeks)
    article_list = Article.objects.filter(create_date__gte=previous_date, is_publish=True)
    article_count = article_list.count()
    if not article_count:
        return {'article_count': article_count, 'status': True, 'result': 'ignore'}
    url_list = [f'{site_full_url()}{each.get_absolute_url()}' for each in article_list]
    status, result = baidu_push('\n'.join(url_list))
    return {'article_count': article_count, 'status': status, 'result': result}


def action_check_site_links(white_domain_list=None):
    """
    校验导航网站有效性，只校验状态为True或者False的，为空的不校验，所以特殊地址可以设置成空跳过校验。

    原来逐个站点串行请求（每个超时 5s），站点多时会把单人 celery worker 长时间占住；
    这里改为有界并发（最多 8 个线程），总耗时不随站点数量线性增长。
    @param white_domain_list: 域名白名单
    @return:
    """
    from concurrent.futures import ThreadPoolExecutor
    from webstack.models import NavigationSite

    white_domain_list = white_domain_list or []
    active_site_list = NavigationSite.objects.filter(is_show__isnull=False)
    active_num = active_site_list.count()
    # 白名单站点直接跳过校验
    sites = [s for s in active_site_list if not white_list_check(white_domain_list, s.link)]

    def check_one(site):
        """返回 'to_not_show' / 'to_show' / None"""
        code, _ = get_link_status(site.link)
        if site.is_show is True:
            if code < 200 or code >= 400:
                site.is_show = False
                site.not_show_reason = f'网页请求返回{code}'
                site.save(update_fields=['is_show', 'not_show_reason'])
                return 'to_not_show'
        else:
            if 200 <= code < 400:
                site.is_show = True
                site.not_show_reason = ''
                site.save(update_fields=['is_show', 'not_show_reason'])
                return 'to_show'
        return None

    to_not_show = 0
    to_show = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        for outcome in pool.map(check_one, sites):
            if outcome == 'to_not_show':
                to_not_show += 1
            elif outcome == 'to_show':
                to_show += 1
    data = {'active_num': active_num, 'to_not_show': to_not_show, 'to_show': to_show}
    return data


def is_current_date_greater_than(input_date_str):
    """
    判断当前日期是否比给定的字符串日期（支持格式为"YYYYMMDD"、"MMDD"、"DD"）大。

    参数:
    input_date_str (str): 表示目标日期的字符串，可以是"YYYYMMDD"、"MMDD"或"DD"格式。

    返回:
    bool: 如果当前日期晚于给定的字符串日期，返回 True；否则返回 False。
    """
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    current_day = current_date.day
    current_hour = current_date.hour

    # 根据输入日期的长度判断格式
    if len(input_date_str) == 10:  # 格式为 YYYYMMDDHH
        try:
            input_date = datetime.strptime(input_date_str, "%Y%m%d%H")
        except ValueError:
            return False
    elif len(input_date_str) == 8:  # 格式为 YYYYMMDD
        try:
            input_date = datetime.strptime(f'{input_date_str}{current_hour}', "%Y%m%d%H")
        except ValueError:
            return False
    elif len(input_date_str) == 4:  # 格式为 MMDD
        try:
            input_date = datetime.strptime(f"{current_year}{input_date_str}{current_hour}",
                                           "%Y%m%d%H")
        except ValueError:
            return False
    elif len(input_date_str) == 2:  # 格式为 DD
        try:
            input_date = datetime.strptime(
                f"{current_year}{current_month:02d}{input_date_str}{current_hour}",
                "%Y%m%d%H")
        except ValueError:
            return False
    else:
        return False

    # 创建当前日期的datetime对象
    current_date_only = datetime(current_year, current_month, current_day, current_hour)

    # 比较当前日期和输入日期
    return current_date_only > input_date


def action_publish_article_by_task(article_ids, filter_rule=None):
    """
    定时将草稿发布出去
    @param article_ids: 需要发布的文章ID
    @param filter_rule: 发布规则，比如 {"140":"0910"} 表示 id为140的文章只有在09月10日之后才发布
    @return:
    """
    from blog.models import Article
    filter_rule = filter_rule or {}
    article_ids = article_ids or []
    data = {}
    for x in filter_rule.keys():
        if x not in article_ids:
            article_ids.append(x)
    for each_id in article_ids:
        if isinstance(each_id, int) or each_id.isdigit():
            article = Article.objects.get(id=int(each_id))
        else:
            article = Article.objects.get(slug=str(each_id))
        if article:
            if article.is_publish is False:
                article.is_publish = True
                if filter_rule.get(str(each_id)):  # 如果设置了规则，则按照规则发布，否则直接发布
                    publish_flag = is_current_date_greater_than(filter_rule.get(str(each_id)))
                    if publish_flag:
                        article.save()
                        data[each_id] = 'Article published successfully'
                    else:
                        data[each_id] = f'Article need publish after {filter_rule.get(str(each_id))}'
                else:
                    article.save()
                    data[each_id] = 'Article published successfully'
            else:
                data[each_id] = 'Article has been published'
        else:
            data[each_id] = 'Article not found'
    return data


def action_write_or_update_view():
    """
    写入或更新当天的文章阅读量
    body:
    {
        "total_views_num": 664512,
        "article_views_num": 664412,
        "page_views_num": 112,
        "article_views": {
            "90": 26,
            "89": 113
        },
        "page_views": {
            "blog:about": 9,
            "blog:friend": 10
        },
        "article_every_hours": {
            "00": 664440,
            "01": 664454
        },
        "page_every_hours": {
            "00": 209,
            "01": 230
        }
    }
    @return:
    """

    date_value = datetime.today().strftime('%Y%m%d')
    this_hour = datetime.now().strftime('%H')
    # 文章计算逻辑
    article_views_num = Article.objects.aggregate(Sum('views'))['views__sum'] or 0
    article_views_dict = {}
    articles = Article.objects.all()
    for article in articles:
        article_views_dict[article.id] = article.views

    # 单页面的统计逻辑
    page_views_dict = {}
    page_views_num = PageView.objects.filter(is_compute=True).aggregate(Sum('views'))[
                         'views__sum'] or 0
    for page in PageView.objects.all():
        page_views_dict[page.url] = page.views

    total_views_num = article_views_num + page_views_num  # 将文章和单页面的总访问量叠加

    body_data = {
        'total_views_num': total_views_num,  # 当前总计=文章总计+单页面总计
        'article_views_num': article_views_num,  # 当前文章阅读总计
        'page_views_num': page_views_num,  # 单页面总计
        'article_views': article_views_dict,  # 当前阅读详情
        'page_views': page_views_dict,  # 单页面的阅读详情
        'article_every_hours': {},  # 当前文章每小时阅读统计
        'page_every_hours': {}  # 当前单页面每小时统计
    }

    # 每小时的数据需要保留历史数据，所以先从历史中拿
    article_every_hours = {}
    page_every_hours = {}
    obj = ArticleView.objects.filter(date=date_value)
    if obj:
        old_body = json.loads(obj.first().body)
        if old_body.get('article_every_hours'):
            article_every_hours = old_body.get('article_every_hours')
        if old_body.get('page_every_hours'):
            page_every_hours = old_body.get('page_every_hours')
    article_every_hours[this_hour] = article_views_num
    page_every_hours[this_hour] = page_views_num
    body_data['article_every_hours'] = article_every_hours
    body_data['page_every_hours'] = page_every_hours

    body = json.dumps(body_data)
    # 写入或更新一条实例
    ArticleView.objects.update_or_create(date=date_value, defaults={'body': body})


class ArticleViewsTool:

    @staticmethod
    def get_last_week_dates():
        """
        获取上周日期列表
        @return:
        """
        today = datetime.today()
        last_monday = today - timedelta(days=(today.weekday() + 7))
        last_week_dates = [last_monday + timedelta(days=i) for i in range(7)]
        # 将日期格式化为字符串，并返回列表
        last_week_dates_str = [date.strftime('%Y%m%d') for date in last_week_dates]
        return last_week_dates_str

    @staticmethod
    def get_this_week_dates():
        """
        获取本周日期列表
        @return:
        """
        today = datetime.today()
        this_monday = today - timedelta(days=today.weekday())
        this_week_dates = [this_monday + timedelta(days=i) for i in range(today.weekday() + 1)]
        # 将日期格式化为字符串，并返回列表
        this_week_dates_str = [date.strftime('%Y%m%d') for date in this_week_dates]
        return this_week_dates_str

    @staticmethod
    def get_day_of_week(date_string):
        # 将输入的日期字符串转换为日期对象
        date_object = datetime.strptime(date_string, '%Y%m%d')
        # 获取星期几的数字（0代表星期一，1代表星期二，以此类推）
        day_of_week = date_object.weekday()
        # 映射数字到星期几的字符串
        days_of_week = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        day_str = days_of_week[day_of_week]

        return day_str

    @staticmethod
    def get_yesterday(date_string):
        # 将输入的日期字符串转换为日期对象
        date_object = datetime.strptime(date_string, '%Y%m%d')
        yesterday = date_object - timedelta(days=1)
        return yesterday.strftime('%Y%m%d')

    @staticmethod
    def get_date_value_by_key(date, key):
        """
        获取一个日期的阅读量总数，没有就返回0
        @param date: 20231208
        @param key: body的参数
        @return: 没有就返回空，所以拿的时候要自行判断类型
        """
        from blog.models import ArticleView
        value = None
        obj = ArticleView.objects.filter(date=date)
        if obj:
            body = json.loads(obj.first().body)
            value = body.get(key)
        if value:
            return value
        else:
            if key in ["total_views_num", "article_views_num", "page_views_num"]:
                return 0
            else:
                return {}

    def get_two_week_data(self):
        """
        从ArticleView模型中获取数据，并分析入库到redis
        @return:
        """

        data = {
            'last_week_views': {},  # 上周数据
            'this_week_views': {},  # 本周数据
        }

        for last_day in self.get_last_week_dates():
            yesterday = self.get_yesterday(last_day)
            last_day_views = self.get_date_value_by_key(last_day, 'total_views_num')
            yesterday_views = self.get_date_value_by_key(yesterday, 'total_views_num')
            if last_day_views and yesterday_views:
                last_day_key = self.get_day_of_week(last_day)
                data['last_week_views'][last_day_key] = last_day_views - yesterday_views
        for this_day in self.get_this_week_dates():
            yesterday = self.get_yesterday(this_day)
            this_day_views = self.get_date_value_by_key(this_day, 'total_views_num')
            yesterday_views = self.get_date_value_by_key(yesterday, 'total_views_num')
            if this_day_views and yesterday_views:
                this_day_key = self.get_day_of_week(this_day)
                data['this_week_views'][this_day_key] = this_day_views - yesterday_views
        return data


def updated_time(feed):
    """
    获取更新时间，获取不到就返回空
    """
    updated_parsed = feed.get('updated_parsed')
    if not updated_parsed:
        return
    try:
        t = updated_parsed
        time = f'{t.tm_year}{t.tm_mon:02d}{t.tm_mday:02d} {t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}'
        # 加8个小时，因为默认是0时区的时间
        time_obj = datetime.strptime(time, '%Y%m%d %H:%M:%S')
        new_time = time_obj + timedelta(hours=8)
        return new_time.strftime('%Y%m%d %H:%M:%S')
    except:
        return


def action_get_feed_data():
    """
    采集feed数据并回写到数据库
    """
    import feedparser
    import requests
    from blog.models import FeedHub

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0'
    }

    result = {}
    feed_items = FeedHub.objects.filter(is_active=True)
    for feed in feed_items:
        try:
            data = {}
            # feedparser.parse(url) 内部不带超时，慢站点会无限期挂住单人 worker；
            # 先用 requests 带超时取回内容，再交给 feedparser 解析
            response = requests.get(feed.url, headers=headers, timeout=8)
            feed_parser = feedparser.parse(response.content)
            entries = [{'title': each['title'], 'link': each['link']} for each in
                       feed_parser['entries']]
            # 如果没有内容就不要去更新之前的数据，避免把数据清空
            if not entries:
                result[feed.name] = 'nok'
                continue
            data['entries'] = entries
            update_time = updated_time(feed_parser.feed)
            if update_time:
                data['updated'] = update_time
            feed.update_data(json.dumps(data, ensure_ascii=False))
            result[feed.name] = 'ok'
        except:
            result[feed.name] = 'nok'
    return result
