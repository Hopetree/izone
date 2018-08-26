# -*- coding: utf-8 -*-

from django.conf import settings

# 自定义上下文管理器
def settings_info(request):
    return {
        'site_end_title':settings.SITE_END_TITLE,
        'site_description':settings.SITE_DESCRIPTION,
        'site_keywords':settings.SITE_KEYWORDS,
        'tool_flag':settings.TOOL_FLAG,
        'api_flag':settings.API_FLAG,
    }