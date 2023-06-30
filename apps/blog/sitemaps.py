# -*- coding: utf-8 -*-
from django.contrib.sitemaps import Sitemap
from .models import Article, Category, Tag
from django.db.models.aggregates import Count
from .utils import site_protocol


class MySitemap(Sitemap):
    protocol = site_protocol()


class ArticleSitemap(MySitemap):
    changefreq = 'weekly'
    priority = 1.0

    def items(self):
        return Article.objects.filter(is_publish=True)

    def lastmod(self, obj):
        return obj.update_date


class CategorySitemap(MySitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Category.objects.filter(article__is_publish=True).annotate(
            total_num=Count('article')).filter(total_num__gt=0)

    def lastmod(self, obj):
        return obj.article_set.first().create_date


class TagSitemap(MySitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Tag.objects.filter(article__is_publish=True).annotate(
            total_num=Count('article')).filter(total_num__gt=0)

    def lastmod(self, obj):
        return obj.article_set.first().create_date
