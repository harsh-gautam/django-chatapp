from django.shortcuts import get_object_or_404
from chat.models import ChatRoom, Contact, Message

def get_last_10_messages(roomObj):
    return Message.objects.by_room(roomObj)

def get_user_contact(username):
    user = get_object_or_404(User, username=username)
    return get_object_or_404(Contact, user=user)

def get_current_chat(room_id):
    return get_object_or_404(ChatRoom, id=chat_id)

def find_room_or_error(room_name):
    return get_object_or_404(ChatRoom, title=room_name)