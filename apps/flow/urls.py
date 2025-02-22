from django.urls import path
from .views import (
    index, create, edit, view,
    process_list, process_detail, process_create, 
    process_update, process_delete
)

app_name = 'flow'

urlpatterns = [
    # 页面路由
    path('', index, name='index'),
    path('create/', create, name='create'),
    path('edit/', edit, name='edit'),
    path('view/', view, name='view'),
    
    # API 路由
    path('api/processes/', process_list, name='process_list'),
    path('api/processes/create/', process_create, name='process_create'),
    path('api/processes/<int:process_id>/', process_detail, name='process_detail'),
    path('api/processes/<int:process_id>/update/', process_update, name='process_update'),
    path('api/processes/<int:process_id>/delete/', process_delete, name='process_delete'),
]
