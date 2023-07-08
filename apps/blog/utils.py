# -*- coding:utf-8 -*-
from datetime import datetime
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.http import JsonResponse
from pygments.formatters.html import HtmlFormatter


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
            result = f"{years}年{remaining_days}天"
        else:
            result = f"{remaining_days}天"

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
