# -*- coding: utf-8 -*-
# 站内搜索改用 MySQL FULLTEXT(n-gram)，替换原 haystack + whoosh 方案
# 注意：该索引依赖 MySQL 5.7.6+ 的 ngram 解析器，用于中文分词检索
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0026_note'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE blog_article ADD FULLTEXT INDEX article_ft_fulltext (title, body, summary) WITH PARSER ngram",
            reverse_sql="ALTER TABLE blog_article DROP INDEX article_ft_fulltext",
        ),
    ]