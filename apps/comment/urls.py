# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import AddcommentView

urlpatterns = [
    url(r'^add/$',AddcommentView,name='add_comment'),
]