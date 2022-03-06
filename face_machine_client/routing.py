# chat/routing.py
from django.urls import re_path as url

from . import consumers

websocket_urlpatterns = [
    url('postman', consumers.FaceWebsocket.as_asgi()),
    url(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
]