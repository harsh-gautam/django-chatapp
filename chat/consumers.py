from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.core.paginator import Paginator

from chat.models import ChatRoomMessage, ChatRoom
from chat.utils import calculate_timestamp
from account.models import Account
import json
import time

class ChatRoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        
        self.room_title = self.scope['url_route']['kwargs']['room_title']
        self.group_name =  f"public_{self.room_title}"
        self.room = await self.find_room_or_error(self.room_title)
        
        # await self.update_user_status_incr(self.scope['user'])  # increment the user's online count
        # Join group
        

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        print("Connected Websocket Group Name: ",self.group_name)
        user = await self.get_user(self.scope['user'])
        await self.connect_user(user)
        participants = await self.get_num_connected_users(self.room_title)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'connected_users_count',
                'connected_users': participants
            }
        )

    async def load_messages(self, data):

        # messages = sync_to_async(self.get_messages()
        await self.send(text_data=json.dumps({'command': 'show_spinner',}))
        payload = await self.get_messages(self.room, data['page_number'])
        if payload['messages'] != None:
            content = {
                'command': 'load_messages',
                'messages': await self.messages_to_json(payload['messages']),
                'new_page_number': payload['new_page_number']
            }
        else:
            content = {
                'command': 'load_messages',
                'messages': None,
                'new_page_number': payload['new_page_number']
            }
        
        await self.send_loaded_messages(content)


    async def new_message(self, data):
        
        sender = data['from']
        message = data['message']
        user = await self.get_user(sender)
        created_message = await self.create_message(user, message, self.room)

        content = {
            'command': 'new_message',
            'message': await self.message_to_json(created_message),
        }
        
        await self.send_chat_message(content)

    async def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(await self.message_to_json(message))
        return result


    async def message_to_json(self, message):
        return{
            'user_id': message.user.id,
            'user': message.user.username,
            'msg_id': message.id,
            'content': message.content,
            'timestamp': calculate_timestamp(message.timestamp),
        }

    
    async def disconnect(self, close_code):
        # await self.update_user_status_decr(self.scope['user'])  
        await self.leave_room(close_code)
        

    async def receive(self, text_data):
        data = json.loads(text_data)
        print("RECIEVED DATA AT BACKEND")
        await self.commands[data['command']](self, data)
    
    
    async def send_chat_message(self, message):
        
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
        print("SENDING MESSAGE TO CLIENT")
        message = event['message']
        await self.send(text_data=json.dumps(message))

    async def leave_room(self, data):
        user = await self.get_user(self.scope['user'])
        await self.disconnect_user(user)
        participants = await self.get_num_connected_users(self.room_title)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'connected_users_count',
                'connected_users': participants
            }
        )

        self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        

    async def connected_users_count(self, event):
        print("ChatConsumer: connected_user_count: count: ", str(event['connected_users']))
        data = {
            'command': 'connected_users',
            'connected_users': event['connected_users']
        }
        await self.send(text_data=json.dumps(data))

    commands = {
        'load_messages': load_messages,
        'new_message': new_message,
        'leave_room': leave_room,
    }
    """
    DATABASE OPERATIONS
    """

    @database_sync_to_async
    def connect_user(self, user):
        return self.room.connect_user(user)

    @database_sync_to_async
    def disconnect_user(self, user):
        return self.room.disconnect_user(user)

    @database_sync_to_async
    def get_messages(self, room, page_number):
        queryset = ChatRoomMessage.objects.filter(room=room).order_by("-timestamp")
        p = Paginator(queryset, 12)

        page_number = int(page_number)
        payload = {}
        if page_number <= p.num_pages:
            payload["messages"] = p.page(page_number).object_list
        else:
            payload["messages"] = None
        payload["new_page_number"] = page_number + 1
        return payload
    
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
