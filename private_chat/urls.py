from django.urls import path

from private_chat.views import (
    private_chat_room_view,
    )

app_name = "private_chat"

urlpatterns = [
    path("chatroom/", private_chat_room_view, name="private-chat-room")
]
