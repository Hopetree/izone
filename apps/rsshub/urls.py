# -*- coding: utf-8 -*-
from django.urls import path
from .views import juejin_hot_articles

urlpatterns = [
    path('juejin/<str:type_id>/<str:category_id>', juejin_hot_articles, name='juejin_hot_articles'),
]
