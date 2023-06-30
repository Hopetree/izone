# -*- coding: utf-8 -*-

from haystack import indexes
from .models import Article


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    views = indexes.IntegerField(model_attr='views')
    # 添加这个字段，可以在查询的时候作为过滤条件，如果不添加则不能用来过滤，新增字段要重新生成索引
    is_publish = indexes.BooleanField(model_attr='is_publish')

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
