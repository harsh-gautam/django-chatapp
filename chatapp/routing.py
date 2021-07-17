from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import re_path

from chat.consumers import ChatRoomConsumer
from private_chat.consumers import PrivateChatConsumer

application = ProtocolTypeRouter(
    {
      "websocket": AllowedHostsOriginValidator(
          AuthMiddlewareStack(
              URLRouter(
                [
                  re_path(
                    r"^ws/chat/room/(?P<room_title>\w+)/$",
                    ChatRoomConsumer.as_asgi(),
                  ),
                  re_path(
                    r"^ws/private/room/(?P<room_id>\w+)/$",
                    PrivateChatConsumer.as_asgi(),
                  ),
                ]
              ),
          ),
      ),
    }
)


# from channels.routing import route
# from chat.consumers import ws_connect, ws_disconnect


# channel_routing = [
#     route('websocket.connect', ws_connect),
#     route('websocket.disconnect', ws_disconnect),
# ]
