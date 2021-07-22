from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.contrib.contenttypes.models import ContentType
import json

from private_chat.exceptions import ClientError
from friends.models import FriendList, FriendRequest
from notification.models import Notification
from notification.utils import LazyNotificationEncoder

class NotificationConsumer(AsyncWebsocketConsumer):

  async def connect(self):
    print("Notification Consumer Connect: ", self.scope['user'])
    await self.accept()

  async def receive(self, text_data):
    data = json.loads(text_data)
    print("Notification Consumer Recieved Data: ", data)
    command = data['command']
    if command is not None:
      await self.commands[command](self, data)
  
  async def disconnect(self, code):
    print("Notification Consumer Disconnect: ", self.scope['user'])

  async def get_general_notifications(self, data):
    user = self.scope['user']
    page_number = data.get("page_number", None)
    try:
      payload = await self.db_get_general_notifications(user, page_number)
      if payload is not None:
        payload = json.loads(payload)
        await self.send_general_notifications(payload["notifications"], payload['new_page_number'])
      else:
        pass
    except ClientError as e:
      self.handle_client_error(e)

  async def send_general_notifications(self, notifications, new_page_number):
    print(notifications, new_page_number)
    await self.send(text_data=json.dumps({
      "msg_type": "0",
      "notifications": notifications,
      "new_page_number": new_page_number,
    }))

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
    "get_general_notifications": get_general_notifications,
  }

  @database_sync_to_async
  def db_get_general_notifications(self, user, page_number):
    """
    Get General Notifications with Pagination (next page of results).
    This is for appending to the bottom of the notifications list.
    General Notifications are:
    1. FriendRequest
    2. FriendList
    """

    if user.is_authenticated:
      friend_req_ct = ContentType.objects.get_for_model(FriendRequest)
      friend_list_ct = ContentType.objects.get_for_model(FriendList)
      notifications = Notification.objects.filter(target=user, content_type__in=[friend_list_ct, friend_req_ct]).order_by("-timestamp")
      
      p = Paginator(notifications, 10)
      payload = {}
      if len(notifications) > 0:
        if(int(page_number)) <= p.num_pages:
          s = LazyNotificationEncoder()
          serialized_notifications = s.serialize(p.page(page_number).object_list)
          payload["notifications"] = serialized_notifications
          payload["new_page_number"] = int(page_number) + 1
      else:
        return None
    else:
      return ClientError('400', 'User must be authenticated.')
    return json.dumps(payload)
