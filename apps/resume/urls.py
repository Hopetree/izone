# -*- coding: utf-8 -*-
from django.urls import path

from .views import ResumeDetailView

urlpatterns = [
    path('<slug:slug>/', ResumeDetailView.as_view(), name='detail')
]
