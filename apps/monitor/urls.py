from django.urls import path
from .views import index, get_server_list, server_push

urlpatterns = [
    path('', index, name='index'),
    path('servers', get_server_list, name='get_server_list'),
    path('server/push', server_push, name='server_push'),
]
