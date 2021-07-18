from django.shortcuts import render, redirect, HttpResponse
from itertools import chain
import json
from .models import PrivateChatRoom, PrivateChatMessage
from .utils import find_or_create_private_chat
from account.models import Account

# Create your views here.
def private_chat_room_view(request, *args, **kwargs):
    user = request.user
    # print(kwargs["room_id"]/
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
    room_id = ""
    room_id = request.GET.get("room_id")
    context = {"room_id": room_id, "m_from_f": m_from_f}
    return render(request, "private_chat/private_room.html", context)

# Ajax call to return a private chatroom or create one if does not exist
def create_or_return_private_chat(request, *args, **kwargs):
  user1 = request.user
  payload = {}
  if user1.is_authenticated:
    if request.method == "POST":
      data = json.loads(request.body)
      user2_id = data["user2_id"]
      try:
        user2 = Account.objects.get(pk=user2_id)
        print("User 1 ID:", user1.id)
        print("User 2 ID:", user2.id)
        chat = find_or_create_private_chat(user1, user2)
        payload['response'] = "Successfully got the chat."
        payload['room_id'] = chat.id
      except Account.DoesNotExist:
        payload['response'] = "Unable to start a chat with that user."
  else:
    payload['response'] = "You can't start a chat if you are not authenticated."
  return HttpResponse(json.dumps(payload), content_type="application/json")
