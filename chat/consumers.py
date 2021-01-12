from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.db.models import F
from django.contrib.auth.models import User

from chat.models import UserProfile, Message
import json

class ChatRoomConsumer(AsyncWebsocketConsumer):

    async def load_messages(self, data):
        print("INSIDE LOAD MESSAGES")
        # messages = sync_to_async(self.get_messages()
        messages = await self.get_messages()
        content = {
            'command': 'load_messages',
            'messages': await self.messages_to_json(messages)
        }
        await self.send_loaded_messages(content)

    async def new_message(self, data):
        print("RECEIVED DATA AT NEW_MESSAGE")
        user = data['from']
        message = data['message']
        author = await self.get_user(user)
        created_message = await self.create_message(author, message)

        content = {
            'command': 'new_message',
            'message': await self.message_to_json(created_message)
        }
    
        await self.send_chat_message(content)


    async def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(await self.message_to_json(message))
        return result


    async def message_to_json(self, message):
        return{
            'author': message.author.username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }

    
    commands = {
        'load_messages': load_messages,
        'new_message': new_message
    }

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
        data = json.loads(text_data)
        print("RECIEVED DATA AT BACKEND")
        await self.commands[data['command']](self, data)
    
    
    async def send_chat_message(self, message):
        print("INSIDE SEND_CHAT_MESSAGE CALLED BY NEW_MESSAGE")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def send_loaded_messages(self, messages):
        await self.send(text_data=json.dumps(messages))


    async def chat_message(self, event):
        print("INSIDE CHAT_MESSAGE")
        message = event['message']
        await self.send(text_data=json.dumps(message))
        print("MESSAGE SEND TO WEBSOCKET")



    """
    DATABASE OPERATIONS
    """
    @database_sync_to_async
    def update_user_status_incr(self, user):
        UserProfile.objects.filter(user=user.pk).update(online=F('online') + 1)

    @database_sync_to_async
    def update_user_status_decr(self, user):
        UserProfile.objects.filter(user=user.pk).update(online=F('online') - 1)

    @database_sync_to_async
    def get_messages(self):
        # return Message.objects.order_by('-timestamp').all()[:10]
        last_messages = reversed(Message.get_last_10_messages())
        return last_messages
    
    @database_sync_to_async
    def create_message(self, user, message):
        created_message = Message.objects.create(author=user, content=message)
        return created_message

    @database_sync_to_async
    def get_user(self, user):
        return User.objects.get(username=user)