from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from private_chat.models import PrivateChatMessage, PrivateChatRoom
from private_chat.exceptions import ClientError
from friends.models import FriendList
from account.models import Account
import json

# from django.core.paginator import Paginator


class PrivateChatConsumer(AsyncWebsocketConsumer):

  async def connect(self):
    room_id = self.scope['url_route']['kwargs']['room_id']
    user = self.scope["user"]
    # print(room_id, user)
    self.accept()  # Let everyone connect
    self.room_id = None

  async def receive(self, data):
    data = json.loads(data)  # Converting recieved data into JSON format
    print(data)
    command = data.get("command", None)
    if command is not None:
        await self.commands[command](self, data)

  async def join_room(self, data):
    room_id = data["room_id"]
    user = self.scope["user"]
    try:
      room = await self.get_room_or_error(room_id, user)
    except ClientError as e:
      raise await self.handle_client_error(e)

    await self.connect_user(room, user)

    self.room_id = room.id
    # await on_user_connected(room, user)

    await self.channel_layer.group_add(
      room.group_name,
      self.channel_name,
    )
    print("user connected to room", self.room_id)

  async def leave_room(self, data):
    pass

  async def get_user_info(self, data):
    pass
  async def send_message(self, data):
    pass
  async def get_room_chat_messages(self, data):
    pass
  async def disconnect(self, close_code):
    print("Private Chat - Disconnected", close_code)
  
  async def handle_client_error(self, e):
    """
    Called when a ClientError is raised.
    Sends error data to UI.
    """
    errorData = {}
    errorData['error'] = e.code
    if e.message:
      errorData['message'] = e.message
      await self.send_message(errorData)
    return

  commands = {
    "leave_room": leave_room,
    "get_user_info": get_user_info,
    "send_message": send_message,
    "get_room_chat_messages": get_room_chat_messages,
  }

  @database_sync_to_async
  def get_room_or_error(self, room_id, user):
    """
    Tries to fetch a room for the user, checking permissions along the way.
    """
    print("INSIDE DATABASE O/P",room_id, user)
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
  def connect_user(self, room, user):
    # add user to connected user list
    account = Account.objects.get(pk=user.id)
    return room.connect_user(account)
  
  @database_sync_to_async
  def disconnect_user(self, room, user):
    # add user to connected user list
    account = Account.objects.get(pk=user.id)
    return room.disconnect_user(account)