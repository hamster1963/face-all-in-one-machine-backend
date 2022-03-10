# chat/routing.py
from django.urls import re_path as url

from . import consumers

websocket_urlpatterns = [
    url('client_api', consumers.FaceWebsocket.as_asgi()),
]