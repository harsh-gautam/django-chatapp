from django.urls import path
from .views import (
    create_room,
    index,
    join_room,
    room,
)

app_name = "chat"

urlpatterns = [
    path('', index, name='chat_home'),
    path('createroom/', create_room, name="createroom"),
    path('joinroom/', join_room, name="joinroom"),
    path('room/<str:room_title>/', room, name='room'),
]