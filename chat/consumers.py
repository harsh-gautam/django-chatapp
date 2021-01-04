from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatRoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        # self.room_group_name = f'chat_%s' % self.room_name

        # Join group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        received_msg = text_data_json['message']
        username = text_data_json['username']
        await self.channel_layer.group_send(self.room_group_name, {'type': 'chat_message', 'message': received_msg, 'username': username})

    async def chat_message(self, event):
        data = {"message": event['message'], "username": event['username']}
        await self.send(json.dumps(data))