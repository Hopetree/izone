# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import (Toolview, BD_pushview, BD_pushview_site, Link_testview,
                    regexview, useragent_view, html_characters,
                    )

urlpatterns = [
    url(r'^$', Toolview, name='total'),  # 工具汇总页
    url(r'^baidu-linksubmit/$', BD_pushview, name='baidu_push'),  # 百度主动推送
    url(r'^baidu-linksubmit-for-sitemap/$', BD_pushview_site, name='baidu_push_site'),  # 百度主动推送sitemap
    url(r'^link-test/$', Link_testview, name='link_test'),  # 友链检测
    url(r'^regex/$', regexview, name='regex'),  # 正则表达式在线
    url(r'^user-agent/$', useragent_view, name='useragent'),  # user-agent生成器
    url(r'^html-special-characters/$', html_characters, name='html_characters'),  # HTML特殊字符查询
]
