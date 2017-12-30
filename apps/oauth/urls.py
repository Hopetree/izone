# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import profile_view, change_profile_view


urlpatterns = [
    url(r'^profile/$',profile_view,name='profile'),
    url(r'^profile/change/$',change_profile_view,name='change_profile'),

]