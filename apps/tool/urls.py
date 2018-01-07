# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import Toolview,BD_pushview,bd_api_view,BD_pushview_site,bd_api_site

urlpatterns = [
    url(r'^$', Toolview, name='total'),  # 工具汇总页
    url(r'^baidu-linksubmit/$',BD_pushview,name='baidu_push'), # 百度主动推送
    url(r'^baidu-linksubmit/api/$',bd_api_view,name='baidu_push_api'), # 百度推送ajax
    url(r'^baidu-linksubmit-for-sitemap/$',BD_pushview_site,name='baidu_push_site'), # 百度主动推送sitemap
    url(r'^baidu-linksubmit-for-sitemap/api/$',bd_api_site,name='baidu_push_api_site'),
]
