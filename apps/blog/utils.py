# -*- coding:utf-8 -*-
import time
import logging
from functools import wraps
from datetime import datetime
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.http import JsonResponse
from pygments.formatters.html import HtmlFormatter

from .models import PageView

logger = logging.getLogger('django')


class CustomHtmlFormatter(HtmlFormatter):
    def __init__(self, lang_str='', **options):
        super().__init__(**options)
        # lang_str has the value {lang_prefix}{lang}
        # specified by the CodeHilite's options
        self.lang_str = lang_str

    def _wrap_code(self, source):
        yield 0, f'<code class="{self.lang_str}">'
        yield from source
        yield 0, '</code>'


class DateCalculator:
    @staticmethod
    def calculate_date_diff(start_date, end_date):
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        diff = end - start
        start_year = start.year

        days = diff.days
        years = 0

        if start.year == end.year:
            remaining_days = days
        else:
            if (start.month > end.month) or (start.month == end.month and start.day > end.day):
                years = end.year - start.year - 1
                last_start = start.replace(year=end.year - 1)
                remaining_days = (end - last_start).days
            else:
                years = end.year - start.year
                last_start = start.replace(year=end.year)
                remaining_days = (end - last_start).days
        if years > 0:
            result = f"{years} 年 {remaining_days} 天"
        else:
            result = f"{remaining_days} 天"

        return result, start_year


def get_site_create_day(create_day):
    """
    返回给的时间到当前日期的年天，create_day格式%Y-%m-%d
    """
    now_day = datetime.now().strftime("%Y-%m-%d")
    return DateCalculator.calculate_date_diff(create_day, now_day)


def site_protocol():
    """
    返回当前使用的协议 http|https，可以给很多需要用到网站完整地址的地方调用
    :return: 当前协议
    """
    protocol = getattr(settings, 'PROTOCOL_HTTPS', 'http')
    return protocol


def site_domain():
    """
    获取当前站点的域名，这个域名实际上是去读数据库的sites表
    settings 配置中需要配置 SITE_ID ，INSTALLED_APPS 中需要添加 django.contrib.sites
    :return: 当前站点域名
    """
    if not django_apps.is_installed('django.contrib.sites'):
        raise ImproperlyConfigured(
            "get site_domain requires django.contrib.sites, which isn't installed.")

    Site = django_apps.get_model('sites.Site')
    current_site = Site.objects.get_current()
    domain = current_site.domain
    return domain


def site_full_url():
    """
    返回当前站点完整地址，协议+域名
    :return:
    """
    protocol = site_protocol()
    domain = site_domain()
    return '{}://{}'.format(protocol, domain)


class ApiResponse(object):
    def __init__(self, code=0, data=None, message="", error=""):
        self.code = code
        self.data = data or {}
        self.message = message
        self.error = error

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def as_dict(self):
        data = {
            'code': self.code,
            'data': self.data,
            'message': self.message,
            'error': self.error
        }
        return data

    def as_json_response(self):
        return JsonResponse(self.as_dict())


class ErrorApiResponse(ApiResponse):
    def __init__(self, code=1, data=None, message="", error=""):
        super().__init__(code, data, message, error)


class RedisKeys:
    """
    配置一些redis的key，其他组件可以引用，避免多个地方使用key不统一的问题
    """
    hot_article_list = 'hot.article.list.{date}'  # 昨日热门文章列表
    hot_tool_list = 'hot.tool.list.{date}'  # 昨日热门工具列表
    week_views_statistics = 'views.week.statistics.{hour}'  # 两周数据
    hours_views_statistics = 'views.hours.statistics.{hour}'  # 两天每小时访问量统计
    month_views_statistics = 'views.month.statistics.{hour}'  # 30天访问量统计
    user_views_statistics = 'views.user.statistics.{hour}'  # 用户总量趋势

    feed_hub_data = 'feed.hub.data.{hour}'  # feed 数据

    # 健康相关
    health_year_data = 'health.year_data.{date}'  # 当年数据，日历图
    heart_rate_interval = 'health.rate_interval.{date}'  # 心率区间分布
    heart_rate_trend = 'health.heart_rate_trend.{date}'  # 心率趋势
    pace_trend = 'health.pace_trend.{date}'  # 配速趋势
    cadence_trend = 'health.cadence_trend.{date}'  # 步频趋势


def check_request_headers(headers_obj):
    """
    校验请求头信息，识别User-Agent过滤掉不合法的请求
    @param headers_obj: request.headers对象
    @return: True 表示请求合法，False 表示请求被过滤
    use: flag = check_request_headers(request.headers)
    """
    # 常见爬虫和自动化工具的黑名单
    user_agent_black_keys = {'spider', 'bot', 'python', 'go-http-client', 'curl', 'yahoo'}

    user_agent = headers_obj.get('user-agent')

    # 如果没有 User-Agent 或 User-Agent 为空，直接返回 False
    if not user_agent:
        return False

    # 转为小写以便进行不区分大小写的匹配
    user_agent_lower = user_agent.lower()

    # 判断是否包含黑名单中的关键字
    if any(key in user_agent_lower for key in user_agent_black_keys):
        logger.warning(f'Bot/Spider request user-agent：{user_agent}')
        return False

    return True


def add_views(url, name=None, is_cache=True):
    """
    单页面访问量统计的视图函数装饰器
    @param is_cache: 是否使用缓存判断访问，跟文章的逻辑一样
    @param name: 页面名称，也可以是描述，方便辨认，没有实际作用
    @param url: 全局唯一，tool:ip这种格式，可以被解析成URL
    @return:
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):

            result = func(request, *args, **kwargs)
            # ******* 浏览量增加的逻辑 *******
            # 仅访问页面的时候才进行计算，接口调用不计算，管理员访问也不计算
            if request.method == "GET" and not request.is_ajax() and not request.user.is_superuser:
                # 获取或者创建一个实例
                # logger.info(request.headers.items())
                if check_request_headers(request.headers):
                    page_views = PageView.objects.filter(url=url)
                    if page_views:
                        obj = page_views.first()
                    else:
                        obj = PageView(url=url, name=name, views=0)
                        obj.save()

                    if is_cache:  # 要判断缓存，则存状态
                        cache_key = f'page_views:read:{url}'
                        is_read_time = request.session.get(cache_key)
                        if not is_read_time:
                            obj.update_views()
                            request.session[cache_key] = time.time()
                        else:
                            t = time.time() - is_read_time
                            if t > 60 * 30:
                                obj.update_views()
                                request.session[cache_key] = time.time()
                    else:
                        obj.update_views()
            # ******* 浏览量增加的逻辑 *******

            return result

        return wrapper

    return decorator
