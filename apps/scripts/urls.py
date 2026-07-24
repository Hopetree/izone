from django.urls import path
from . import views

app_name = 'scripts'

urlpatterns = [
    path('', views.ScriptListView.as_view(), name='list'),
    path('publish/', views.publish_script, name='publish'),
    path('<slug:slug>/', views.ScriptDetailView.as_view(), name='detail'),
    path('<slug:slug>/raw/', views.script_raw, name='raw'),
]
