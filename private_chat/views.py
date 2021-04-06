from django.shortcuts import render, redirect
from itertools import chain
from .models import PrivateChatRoom, PrivateChatMessage

# Create your views here.
def private_chat_room_view(request, *args, **kwargs):
    user = request.user

    if not user.is_authenticated:
        return redirect("account:login")

    # Find all the rooms whose user is a part of
    rooms1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
    rooms2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)

    # Join both rooms
    rooms = list(chain(rooms1, rooms2))

    # message from friend (m_from_f)
    # it denotes the recent message from the friends

    m_from_f = []
    for room in rooms:
        if room.user1 == user:
            friend = room.user2
        else:
            friend = room.user1

        m_from_f.append({"message": "", "friend": friend})

    context = {"room_title": kwargs.get("room_title"), "m_from_f": m_from_f}
    return render(request, "private_chat/private_room.html", context)