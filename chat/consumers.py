from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import UserProfile

from django.db.models import F
import json

class ChatRoomConsumer(AsyncWebsocketConsumer):

    async def fetch_messages(self, data):
        pass

    async def new_message(self, data):
        pass


    async def connect(self):
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        await self.update_user_status_incr(self.scope['user'])  # increment the user's online count

        # Join group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    
    async def disconnect(self, close_code):
        await self.update_user_status_decr(self.scope['user'])  # Decrement the user's online count
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        received_msg = text_data_json['message']
        username = text_data_json['username']
        await self.channel_layer.group_send(self.room_group_name, {'type': 'chat_message', 'message': received_msg, 'username': username, 'is_logged_in': True})

    async def chat_message(self, event):
        data = {"message": event['message'], "username": event['username']}
        await self.send(json.dumps(data))

    @database_sync_to_async
    def update_user_status_incr(self, user):
        UserProfile.objects.filter(user=user.pk).update(online=F('online') + 1)

    @database_sync_to_async
    def update_user_status_decr(self, user):
        UserProfile.objects.filter(user=user.pk).update(online=F('online') - 1)