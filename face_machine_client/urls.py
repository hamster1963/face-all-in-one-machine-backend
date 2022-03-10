# chat/urls.py
from django.urls import re_path as url
from django.urls import path

from . import views

urlpatterns = [
    path('admin', views.client_register, name='设备注册'),
    path('push', views.push_to_client, name='信息下发'),

]