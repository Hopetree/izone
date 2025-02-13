from django.urls import path
from .views import index, create, edit, view

urlpatterns = [
    path('', index, name='index'),
    path('create/', create, name='create'),
    path('edit/', edit, name='edit'),
    path('view/', view, name='view'),
]
