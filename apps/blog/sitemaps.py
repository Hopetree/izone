# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from .models import Article, Category, Tag
from django.db.models.aggregates import Count


class MySitemap(object):
    protocol = getattr(settings, 'PROTOCOL_HTTPS', 'http')


class ArticleSitemap(MySitemap, Sitemap):
    changefreq = 'weekly'
    priority = 1.0

    def items(self):
        return Article.objects.all()

    def lastmod(self, obj):
        return obj.update_date


class CategorySitemap(MySitemap, Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Category.objects.annotate(total_num=Count('article')).filter(total_num__gt=0)

    def lastmod(self, obj):
        return obj.article_set.first().create_date


class TagSitemap(MySitemap, Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Tag.objects.annotate(total_num=Count('article')).filter(total_num__gt=0)

    def lastmod(self, obj):
        return obj.article_set.first().create_date
