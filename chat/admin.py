from django.contrib import admin
from chat.models import ChatRoom, ChatRoomMessage

admin.site.register((ChatRoom, ChatRoomMessage))
