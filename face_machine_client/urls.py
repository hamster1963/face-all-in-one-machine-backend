# chat/urls.py
from django.urls import re_path as url
from django.urls import path

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<room_name>[^/]+)/$', views.room, name='room'),
    path('', views.client_register, name='设备注册')
]