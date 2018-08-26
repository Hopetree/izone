"""izone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView

from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import ArticleSitemap, CategorySitemap, TagSitemap
from blog.feeds import AllArticleRssFeed

from rest_framework.routers import DefaultRouter
from api import views as api_views

if settings.API_FLAG:
    router = DefaultRouter()
    router.register(r'users',api_views.UserListSet)
    router.register(r'articles',api_views.ArticleListSet)
    router.register(r'tags',api_views.TagListSet)
    router.register(r'categorys',api_views.CategoryListSet)
    router.register(r'timelines',api_views.TimelineListSet)
    router.register(r'toollinks',api_views.ToolLinkListSet)

# 网站地图
sitemaps = {
    'articles': ArticleSitemap,
    'tags': TagSitemap,
    'categories': CategorySitemap
}

urlpatterns = [
    url(r'^adminx/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),  # allauth
    url(r'^accounts/', include('oauth.urls', namespace='oauth')),  # oauth,只展现一个用户登录界面
    url('', include('blog.urls', namespace='blog')),  # blog
    url(r'^comment/',include('comment.urls',namespace='comment')), # comment
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')), # robots
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'), # 网站地图
    url(r'^feed/$', AllArticleRssFeed(), name='rss'),   # rss订阅
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 加入这个才能显示media文件

if settings.API_FLAG:
    urlpatterns.append(url(r'^api/v1/',include(router.urls,namespace='api')))    # restframework

if settings.TOOL_FLAG:
    urlpatterns.append(url(r'^tool/', include('tool.urls',namespace='tool')))    # tool