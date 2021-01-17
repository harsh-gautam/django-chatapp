from django.urls import path
from friends.views import (
    send_friend_request,
    accept_friend_request,
    decline_friend_request,
    cancel_friend_request,
    remove_friend,
    )

app_name = "friends"

urlpatterns = [
    path('accept-friend-request/', accept_friend_request, name="accept-friend-req"),
    path('cancel-friend-request/', cancel_friend_request, name="cancel-friend-req"),
    path('decline-friend-request/', decline_friend_request, name="decline-friend-req"),
    path('remove-friend/', remove_friend, name="remove-friend"),
    path('send-friend-request/', send_friend_request, name="send-friend-req"),
]
