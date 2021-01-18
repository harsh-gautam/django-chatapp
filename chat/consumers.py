from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.db.models import F

from chat.models import ChatRoomMessage, ChatRoom
from account.models import Account
# from chat.utils import get_last_10_messages
import json

class ChatRoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        
        self.room_title = self.scope['url_route']['kwargs']['room_title']
        self.group_name =  f"public_{self.room_title}"
        self.room = await self.find_room_or_error(self.room_title)
        
        # await self.update_user_status_incr(self.scope['user'])  # increment the user's online count
        # Join group
        print("Websocket Group Name: ",self.group_name)

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        participants = await self.get_num_connected_users(self.room_title)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'connected_users_count',
                'connected_users': participants
            }
        )

    async def load_messages(self, data):
        print("INSIDE LOAD MESSAGES")
        # messages = sync_to_async(self.get_messages()
        messages = await self.get_messages(self.room)
        content = {
            'command': 'load_messages',
            'messages': await self.messages_to_json(messages),
        }
        await self.send_loaded_messages(content)


    async def new_message(self, data):
        print("RECEIVED DATA AT NEW_MESSAGE")
        sender = data['from']
        message = data['message']
        user = await self.get_user(sender)
        created_message = await self.create_message(user, message, self.room)

        content = {
            'command': 'new_message',
            'message': await self.message_to_json(created_message),
        }
        print("Content Loaded to Send: ", content)
        await self.send_chat_message(content)

    async def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(await self.message_to_json(message))
        return result


    async def message_to_json(self, message):
        return{
            'user': message.user.username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }

    
    commands = {
        'load_messages': load_messages,
        'new_message': new_message
    }



    
    async def disconnect(self, close_code):
        # await self.update_user_status_decr(self.scope['user'])  

        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        participants = await self.get_num_connected_users(self.room_title)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'connected_users_count',
                'connected_users': participants
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        print("RECIEVED DATA AT BACKEND")
        await self.commands[data['command']](self, data)
    
    
    async def send_chat_message(self, message):
        print("INSIDE SEND_CHAT_MESSAGE CALLED BY NEW_MESSAGE")
        await self.channel_layer.group_send(
            self.group_name,
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


    async def connected_users_count(self, event):
        print("ChatConsumer: connected_user_count: count: ", str(event['connected_users']))
        data = {
            'command': 'connected_users',
            'connected_users': event['connected_users']
        }
        await self.send(text_data=json.dumps(data))


    """
    DATABASE OPERATIONS
    """

    @database_sync_to_async
    def get_messages(self, room):
        # return Message.objects.order_by('-timestamp').all()[:10]
        return reversed(ChatRoomMessage.get_room_messages(room))
    
    @database_sync_to_async
    def create_message(self, user, message, room):
        created_message = ChatRoomMessage.objects.create(user=user, content=message, room=room)
        return created_message

    @database_sync_to_async
    def get_user(self, user):
        return Account.objects.get(username=user)

    @database_sync_to_async
    def get_num_connected_users(self, room_title):
        # room = self.find_room_or_error(room_title)
        room = ChatRoom.objects.get(title=room_title)
        if room.participants:
            return len(room.participants.all())

    @database_sync_to_async
    def find_room_or_error(self, room_title):
        return ChatRoom.objects.get(title=room_title)
