from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers import serialize
from django.utils import timezone
from django.core.paginator import Paginator
import json

from private_chat.models import PrivateChatMessage, PrivateChatRoom
from private_chat.exceptions import ClientError
from private_chat.utils import LazyRoomChatMessageEncoder, calculate_timestamp
from private_chat.constants import *

from friends.models import FriendList

from account.models import Account
from account.utils import LazyAccountEncoder

# from django.core.paginator import Paginator


class PrivateChatConsumer(AsyncWebsocketConsumer):

  # Connect to the Consumer
  async def connect(self):
    print("Private Chat Consumer Connect: ", self.scope['user'])
    await self.accept()  # Let everyone connect
    self.room_id = None

  # Disconnect from Consumer
  async def disconnect(self, close_code):
    try:
      if self.room_id != None:
        await self.leave_room(self.room_id)
    except Exception as e:
      print("Exception Occured ", e) 

  # Received a message from client
  async def receive(self, text_data):
    data = json.loads(text_data)  # Converting recieved data into JSON format
    command = data.get("command", None)
    try:
      if command is not None:
          await self.commands[command](self, data)
    except ClientError as e:
      await self.handle_client_error(e)
  
  # Join a chat
  async def join_room(self, data):
    ''' Called by receive() method when someone tries to join a room'''

    id = data["room_id"]
    user = self.scope["user"]
    try:
      room = await self.get_room_or_error(id, user)
    except ClientError as e:
      return await self.handle_client_error(e)

    await self.connect_user(room, user)

    self.room_id = room.id
    # await on_user_connected(room, user)

    await self.channel_layer.group_add(
      room.group_name,
      self.channel_name,
    )

    # Infrom client that chat is connected
    await self.send(text_data=json.dumps({
			"join": str(room.id),
		}))
    
    # Notify Consumer Group that someone has joined
    if user.is_authenticated:
      await self.channel_layer.group_send(
        room.group_name,
        {
          "type": "chat.join",
          "room_id": room.id,
          "profile_image": user.profile_image.url,
          "username": user.username,
          "user_id": user.id,
        }
      )
    
    print("User Connect to Room ", self.room_id)


  async def send_room(self, data):
    ''' Called by receive() when someone sends a message in room'''
    room_id = data["room_id"]
    message = data["message"]
    if len(message.lstrip()) == 0:
      raise ClientError("422", "You can't send an empty message")
    
    if self.room_id != None:
      print("SELF ROOM ID: ", self.room_id)
      print("ROOM ID: ", room_id)
      if str(room_id) != str(self.room_id):
        print("SELF ROOM ID AND ROOM ID DOES NOT MATCH")
        raise ClientError("ROOM_ACCESS_DENIED", "Room access denied.")
    else:
      print("SELF ROOM ID IS NONE")
      raise ClientError("ROOM_ACCESS_DENIED", "Room access denied.")
    
    room = await self.get_room_or_error(room_id, self.scope["user"])

    await self.create_room_message(room, self.scope['user'], message)

    await self.channel_layer.group_send(
      room.group_name,
      {
        "type": "chat.message",
        "profile_image": self.scope['user'].profile_image.url,
        "username": self.scope['user'].username,
        "user_id": self.scope['user'].id,
        "message": message
      }
    )  


  async def leave_room(self, room_id):
    user = self.scope["user"]
    room = await self.get_room_or_error(room_id, user)

    # Notify the group that someone has left
    await self.channel_layer.group_send(
      room.group_name,
      {
        "type":"chat.leave",
        "room_id": room_id,
        "profile_image": self.scope["user"].profile_image.url,
        "username": self.scope["user"].username,
        "user_id": self.scope["user"].id
      }
    )
    # Remove from room
    self.room_id = None
    await self.channel_layer.group_discard(
      room.group_name,
      self.channel_name,
    )

    await self.send(text_data=json.dumps({"leave": str(room_id)}))
    print("Private Chat - Disconnected") 


  # These helper methods are named by the types we send - so chat.join becomes chat_join
  async def chat_join(self, event):
    """
    Called when someone has joined our chat.
    """
    # Send a message down to the client
    print("ChatConsumer: chat_join: " + str(self.scope["user"].id))
    if event["username"]:
      await self.send(text_data=json.dumps(
        {
          "msg_type": MSG_TYPE_ENTER,
          "room": event["room_id"],
          "profile_image": event["profile_image"],
          "username": event["username"],
          "user_id": event["user_id"],
          "message": event["username"] + " is online.",
        },)
      )


  async def chat_leave(self, event):
    """
    Called when someone has left our chat.
    """
    # Send a message down to the client
    print("ChatConsumer: chat_leave")
    if event["username"]:
      await self.send(text_data=json.dumps(
      {
        "msg_type": MSG_TYPE_LEAVE,
        "room": event["room_id"],
        "username": event["username"],
        "user_id": event["user_id"],
        "message": event["username"] + " is offline.",
      },)
    )


  async def chat_message(self, event):
    """
    Called when someone has messaged our chat.
    """
    # Send a message down to the client
    print("ChatConsumer: chat_message")
    timestamp = calculate_timestamp(timezone.now())
    await self.send(text_data=json.dumps(
      {
        "msg_type": MSG_TYPE_MESSAGE,
        "username": event['username'],
        'user_id': event['user_id'],
        'message': event['message'],
        'timestamp': timestamp
      }
    ))


  async def get_user_info(self, data):
    user = self.scope["user"]
    room = await self.get_room_or_error(data["room_id"], user)
    try:
      other_user = room.user1
      if other_user == user:
        other_user = room.user2
      payload = {}
      s = LazyAccountEncoder()
      payload['user_info'] = s.serialize([other_user])[0]
      await self.send_user_info_payload(payload['user_info'])
    except Exception as e:
      print("EXCEPTION: " + str(e))

  async def send_user_info_payload(self, user_info):
    """
    Send a payload of user information to the ui
    """
    print("ChatConsumer: send_user_info_payload. ")
    await self.send(text_data=json.dumps(
      {
        "user_info": user_info,
      },)
    )


  async def get_chat_room_messages(self, data):
    room_id = data['room_id']
    page_number = data['page_number']
    user = self.scope['user']
    room = await self.get_room_or_error(room_id, user)
    payload = await self.get_room_messages(room, page_number)
    if payload != None:
      payload = json.loads(payload)
      await self.send_messages_payload(payload['messages'], payload['new_page_number'])
    else:
      raise ClientError('204', "Something went wrong while fetching room messages.")

  async def send_messages_payload(self, messages, new_page_number):
    '''Send a payload of messages to UI'''
    await self.send(text_data=json.dumps(
      {
        'messages_payload' : 'messages_payload',
        'messages': messages,
        'new_page_number': new_page_number
      }
    ))

  async def display_progress_bar(self, is_displayed):
    """
    1. is_displayed = True
      - Display the progress bar on UI
    2. is_displayed = False
      - Hide the progress bar on UI
    """
    print("DISPLAY PROGRESS BAR: " + str(is_displayed))

  
  async def handle_client_error(self, e):
    """
    Called when a ClientError is raised.
    Sends error data to UI.
    """
    errorData = {}
    errorData['error'] = e.code
    if e.message:
      errorData['message'] = e.message
      await self.send(text_data=json.dumps(errorData))
    return


  commands = {
    "join_room": join_room,
    "leave_room": leave_room,
    "get_user_info": get_user_info,
    "send_room": send_room,
    "get_chat_room_messages": get_chat_room_messages,
  }

  @database_sync_to_async
  def get_room_or_error(self, room_id, user):
    """
    Tries to fetch a room for the user, checking permissions along the way.
    """
    try:
      room = PrivateChatRoom.objects.get(pk=room_id)
    except PrivateChatRoom.DoesNotExist:
      raise ClientError("ROOM_INVALID", "Invalid room.")

    # Is this user allowed in the room? (must be user1 or user2)
    if user != room.user1 and user != room.user2:
      raise ClientError("ROOM_ACCESS_DENIED", "You do not have permission to join this room.")

    # Are the users in this room friends?
    friend_list = FriendList.objects.get(user=user).friends.all()
    if not room.user1 in friend_list:
      if not room.user2 in friend_list:
        raise ClientError("ROOM_ACCESS_DENIED", "You must be friends to chat.")
    return room

  @database_sync_to_async
  def get_room_messages(self, room, page_number):
    try:
      qs = PrivateChatMessage.objects.by_room(room)
      p = Paginator(qs, DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)
      
      payload = {}
      messages_data = None
      new_page_number = int(page_number)
      if new_page_number <= p.num_pages:
        new_page_number += new_page_number
        s = LazyRoomChatMessageEncoder()
        payload["messages"] = s.serialize(p.page(page_number).object_list)
      else:
        payload["messages"] = "None"
      payload["new_page_number"] = new_page_number
      return json.dumps(payload)
    except Exception as e:
      print("Exception : ", e)
      return None

  @database_sync_to_async
  def connect_user(self, room, user):
    # add user to connected user list
    account = Account.objects.get(pk=user.id)
    return room.connect_user(account)
  
  @database_sync_to_async
  def disconnect_user(self, room, user):
    # add user to connected user list
    account = Account.objects.get(pk=user.id)
    return room.disconnect_user(account)
  
  @database_sync_to_async
  def create_room_message(self, room, user, message):
    return PrivateChatMessage.objects.create(user=user, room=room, content=message)