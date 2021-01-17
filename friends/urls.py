from django.urls import path
from friends.views import (
    send_friend_request,
    accept_friend_request,
    )

app_name = "friends"

urlpatterns = [
    path('send-friend-request/', send_friend_request, name="send-friend-req"),
    path('accept-friend-request/', accept_friend_request, name="accept-friend-req"),
]
