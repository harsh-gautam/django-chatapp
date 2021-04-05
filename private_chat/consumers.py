from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

# from django.core.paginator import Paginator


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.room_title = self.scope["url_route"]["kwargs"]["room_title"]
        self.group_name = f"public_{self.room_title}"
        print(self.room_title)
