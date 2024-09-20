# -*- coding: utf-8 -*-
import datetime
import json
from django.conf import settings
from .utils import (site_full_url, get_site_create_day)
from blog.models import SiteConfig

# 静态文件版本（只收集常改的，不常改的直接在页面改），每次更新了静态文件就更新一下这个版本
# todo 可以做成自动化，每次拉git代码的时候检查是否更新了某个静态文件，自动更新版本
STATIC_VERSION = {
    'css_blog_base': '20240305.02',
    'css_blog_detail': '20240324.01',
    'css_blog_night': '20240615.01',

    'js_blog_base': '20240305.01',
    'js_blog_article': '20240115.01',
    'js_blog_code': '20240129.02',

    'css_tool_tool': '20240115.01',
    'js_tool_tool': '20240115.01',
}


# 自定义上下文管理器
def settings_info(request):
    """
    上下文的属性值优先从网站配置模型读取，然后是环境变量，最后是默认值
    @param request:
    @return:
    """
    # 尝试获取唯一的 SiteConfig 实例，如果不存在则返回 None
    try:
        site_config = SiteConfig.objects.first()
        config_data = json.loads(site_config.config_data)
    except SiteConfig.DoesNotExist:
        config_data = {}

    site_create_date = config_data.get('site_create_date', settings.SITE_CREATE_DATE)
    site_create_date_info = get_site_create_day(site_create_date)
    return {
        'this_year': datetime.datetime.now().year,
        'site_create_date': site_create_date_info[0],
        'site_create_year': site_create_date_info[1],

        'site_logo_name': config_data.get('site_logo_name', settings.SITE_LOGO_NAME),
        'site_end_title': config_data.get('site_end_title', settings.SITE_END_TITLE),
        'site_description': config_data.get('site_description', settings.SITE_DESCRIPTION),
        'site_keywords': config_data.get('site_keywords', settings.SITE_KEYWORDS),
        'cnzz_protocol': config_data.get('site_cnzz_protocol', settings.CNZZ_PROTOCOL),
        '51la': config_data.get('site_la51_protocol', settings.LA51_PROTOCOL),
        'beian': config_data.get('site_icp_number', settings.BEIAN),
        'my_github': config_data.get('site_github', settings.MY_GITHUB),
        'site_verification': config_data.get('site_verification', settings.MY_SITE_VERIFICATION),
        'reward_wx': config_data.get('site_reward_wx', settings.REWARD_WX),
        'reward_zfb': config_data.get('site_reward_zfb', settings.REWARD_ZFB),

        'site_url': site_full_url(),
        'static_version': STATIC_VERSION,
        'tool_flag': settings.TOOL_FLAG,
        'api_flag': settings.API_FLAG,
    }
