# -*- coding: utf-8 -*-
from django.urls import path
from .views import (juejin_hot_articles,
                    cnblogs_pick,
                    github_issues_ryf)

urlpatterns = [
    path('juejin/<str:type_id>/<str:category_id>', juejin_hot_articles, name='juejin_hot_articles'),
    path('cnblogs/pick', cnblogs_pick, name='cnblogs_pick'),
    path('ruanyf/weekly/issues', github_issues_ryf, name='github_issues_ryf'),
]
