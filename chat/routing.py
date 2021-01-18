from django.urls import re_path
from .consumers import ChatRoomConsumer

websocket_urlpatterns = [
    re_path(r'^ws/chat/room/(?P<room_title>\w+)/$', ChatRoomConsumer.as_asgi()),
]