# -*- coding:utf-8 -*-
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


def site_protocol():
    '''
    返回当前使用的协议 http|https，可以给很多需要用到网站完整地址的地方调用
    :return: 当前协议
    '''
    protocol = getattr(settings, 'PROTOCOL_HTTPS', 'http')
    return protocol


def site_domain():
    '''
    获取当前站点的域名，这个域名实际上是去读数据库的sites表
    settings 配置中需要配置 SITE_ID ，INSTALLED_APPS 中需要添加 django.contrib.sites
   :return: 当前站点域名
    '''
    if not django_apps.is_installed('django.contrib.sites'):
        raise ImproperlyConfigured("get site_domain requires django.contrib.sites, which isn't installed.")

    Site = django_apps.get_model('sites.Site')
    current_site = Site.objects.get_current()
    domain = current_site.domain
    return domain


def site_full_url():
    '''
    返回当前站点完整地址，协议+域名
    :return:
    '''
    protocol = site_protocol()
    domain = site_domain()
    return '{}://{}'.format(protocol, domain)
