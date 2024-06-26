from django.urls import path
from .views import (index,
                    demo,
                    get_server_list,
                    get_server_list_for_demo,
                    server_push)

urlpatterns = [
    path('', index, name='index'),
    path('demo', demo, name='demo'),
    path('servers', get_server_list, name='get_server_list'),
    path('servers/demo', get_server_list_for_demo, name='get_server_list_for_demo'),
    path('server/push', server_push, name='server_push'),
]
