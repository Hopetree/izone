# -*- coding: utf-8 -*-
import datetime
import json
from django.conf import settings
from .utils import (site_full_url, get_site_create_day)

# 静态文件版本（只收集常改的，不常改的直接在页面改），每次更新了静态文件就更新一下这个版本
# todo 可以做成自动化，每次拉git代码的时候检查是否更新了某个静态文件，自动更新版本
STATIC_VERSION = {
    'css_blog_base': '20240305.02',
    'css_blog_detail': '20240131.01',
    'css_blog_night': '20240115.01',

    'js_blog_base': '20240305.01',
    'js_blog_article': '20240115.01',
    'js_blog_code': '20240129.02',

    'css_tool_tool': '20240115.01',
    'js_tool_tool': '20240115.01',
}


# 自定义上下文管理器
def settings_info(request):
    site_create_day = get_site_create_day(settings.SITE_CREATE_DATE)
    return {
        'this_year': datetime.datetime.now().year,
        'site_create_date': site_create_day[0],
        'site_create_year': site_create_day[1],
        'site_logo_name': settings.SITE_LOGO_NAME,
        'site_end_title': settings.SITE_END_TITLE,
        'site_description': settings.SITE_DESCRIPTION,
        'site_keywords': settings.SITE_KEYWORDS,
        'tool_flag': settings.TOOL_FLAG,
        'api_flag': settings.API_FLAG,
        'cnzz_protocol': settings.CNZZ_PROTOCOL,
        '51la': settings.LA51_PROTOCOL,
        'beian': settings.BEIAN,
        'my_github': settings.MY_GITHUB,
        'site_verification': settings.MY_SITE_VERIFICATION,
        'site_url': site_full_url(),
        'private_links': json.loads(settings.PRIVATE_LINKS),
        'static_version': STATIC_VERSION,
    }
