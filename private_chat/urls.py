from django.urls import path

from private_chat.views import (
    private_chat_room_view,
)

app_name = "private_chat"

urlpatterns = [
    path("room/<str:room_title>/", private_chat_room, name="private-chat-room")
]
