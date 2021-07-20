from channels.generic.websocket import AsyncWebsocketConsumer
import json

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