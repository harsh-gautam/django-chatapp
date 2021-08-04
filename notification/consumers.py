from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.contrib.contenttypes.models import ContentType
import json
from datetime import datetime

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
      print("NOTIFICATION PAYLOAD TO SEND: ", payload)
      if payload is not None:
        payload = json.loads(payload)
        await self.send_general_notifications(payload["notifications"], payload['new_page_number'])
      else:
        await self.send(text_data=json.dumps({"msg_type": 2}))
    except ClientError as e:
      self.handle_client_error(e)

  async def send_general_notifications(self, notifications, new_page_number):
    print(notifications, new_page_number)
    await self.send(text_data=json.dumps({
      "msg_type": "0",
      "notifications": notifications,
      "new_page_number": new_page_number,
    }))

  async def handle_friend_request(self, data):
    notification_id = data.get("notification_id", None)
    if(data['type'] == 'accept'):
      if notification_id is not None:
        try:
          payload = await self.db_accept_request(self.scope['user'], notification_id)
          if payload is not None:
            payload = json.loads(payload)
            await self.send_updated_notification(payload['notification'])
          else:
            raise ClientError("ERROR_HANDLING_FRIEND_REQUEST", "Something went wrong. Try refreshing the browser.")
        except ClientError as e:
          await self.handle_client_error(e)
    else:
      if notification_id is not None:
        try:
          payload = await self.db_decline_request(self.scope['user'], notification_id)
          if payload is not None:
            payload = json.loads(payload)
            await self.send_updated_notification(payload['notification'])
          else:
            raise ClientError("ERROR_HANDLING_FRIEND_REQUEST", "Something went wrong. Try refreshing the browser.")
        except ClientError as e:
          await self.handle_client_error(e)
  
  async def send_updated_notification(self, notification):
    await self.send(text_data=json.dumps({
      "msg_type": 1,
      "notification": notification,
    }))

  async def refresh_general_notifications(self, data):
    payload = await self.db_refresh_general_notifications(self.scope["user"], data['oldest_timestamp'], data['newest_timestamp'])
    if payload == None:
      raise ClientError("ERROR", "Something went wrong.")
    else:
      payload = json.loads(payload)
      await self.send_refreshed_general_notifications(payload["notifications"])

  async def send_refreshed_general_notifications(self, notifications):
    await self.send(text_data=json.dumps({
      "msg_type": 3,
      "notifications": notifications,
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
    "handle_friend_request": handle_friend_request,
    "refresh_general_notifications": refresh_general_notifications,
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
          return json.dumps(payload)
      else:
        return None
    else:
      raise ClientError('400', 'User must be authenticated.')

  @database_sync_to_async
  def db_accept_request(self, user, notification_id):
    # Accept Friend Request
    payload = {}
    if user.is_authenticated:
      try:
        notification = Notification.objects.get(pk=notification_id)
        friend_request = notification.content_object

        if friend_request.receiver == user:
          updated_notification = friend_request.accept()
          s = LazyNotificationEncoder()
          payload['notification'] = s.serialize([updated_notification])[0]
          return json.dumps(payload)
      except Notification.DoesNotExist:
        raise ClientError("ERROR_NOTIFICATOIN", "An error occurred. Try refreshing the browser.")
    return None

  @database_sync_to_async
  def db_decline_request(self, user, notification_id):
    # Decline Friend Request
    payload = {}
    if user.is_authenticated:
      try:
        notification = Notification.objects.get(pk=notification_id)
        friend_request = notification.content_object

        if friend_request.receiver == user:
          updated_notification = friend_request.decline()
          s = LazyNotificationEncoder()
          payload['notification'] = s.serialize([updated_notification])[0]
          return json.dumps(payload)
      except Notification.DoesNotExist:
        raise ClientError("ERROR_NOTIFICATOIN", "An error occurred. Try refreshing the browser.")

  @database_sync_to_async
  def db_refresh_general_notifications(self, user, oldest_timestamp, newest_timestamp):
    """
    Retrieve the general notifications newer than the oldest one on the screen and younger than the newest one the screen.
    The result will be: Notifications currently visible will be updated
    """
    payload = {}
    if user.is_authenticated:
      oldest_ts = oldest_timestamp[0:oldest_timestamp.find("+")] # remove timezone because who cares
      oldest_ts = datetime.strptime(oldest_ts, '%Y-%m-%d %H:%M:%S.%f')
      newest_ts = newest_timestamp[0:newest_timestamp.find("+")] # remove timezone because who cares
      newest_ts = datetime.strptime(newest_ts, '%Y-%m-%d %H:%M:%S.%f')
      friend_request_ct = ContentType.objects.get_for_model(FriendRequest)
      friend_list_ct = ContentType.objects.get_for_model(FriendList)
      notifications = Notification.objects.filter(target=user, content_type__in=[friend_request_ct, friend_list_ct], timestamp__gte=oldest_ts, timestamp__lte=newest_ts).order_by('-timestamp')

      s = LazyNotificationEncoder()
      payload['notifications'] = s.serialize(notifications)
    else:
      raise ClientError("User must be authenticated to get notifications.")

    return json.dumps(payload) 
