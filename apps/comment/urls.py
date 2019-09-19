# -*- coding: utf-8 -*-
from django.urls import path
from .views import AddcommentView, NotificationView, mark_to_read, mark_to_delete

urlpatterns = [
    path('add/', AddcommentView, name='add_comment'),
    path('notification/', NotificationView, name='notification'),
    path('notification/no-read/', NotificationView, {'is_read': 'false'}, name='notification_no_read'),
    path('notification/mark-to-read/', mark_to_read, name='mark_to_read'),
    path('notification/mark-to-delete/', mark_to_delete, name='mark_to_delete'),
]
