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
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic import RedirectView

from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import ArticleSitemap, CategorySitemap, TagSitemap
from blog.feeds import AllArticleRssFeed
from blog.views import robots

# 网站地图
sitemaps = {
    'articles': ArticleSitemap,
    'tags': TagSitemap,
    'categories': CategorySitemap
}

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/blog/img/favicon.ico')),
    path('adminx/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # allauth
    path('accounts/', include(('oauth.urls', 'oauth'), namespace='oauth')),  # oauth,只展现一个用户登录界面
    path('', include(('blog.urls', 'blog'), namespace='blog')),  # blog
    path('comment/',include(('comment.urls', 'comment'),namespace='comment')), # comment
    path('robots.txt', robots, name='robots'), # robots
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'), # 网站地图
    path('feed/', AllArticleRssFeed(), name='rss'),   # rss订阅
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 加入这个才能显示media文件

if settings.API_FLAG:
    from api.urls import router
    urlpatterns.append(path('api/v1/',include((router.urls, router.root_view_name),namespace='api')))    # restframework

if settings.TOOL_FLAG:
    urlpatterns.append(path('tool/', include(('tool.urls', 'tool'),namespace='tool')))    # tool