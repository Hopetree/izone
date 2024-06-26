from django.urls import path
from .views import PortView

urlpatterns = [
    path('', PortView.as_view(), name='index'),
]
