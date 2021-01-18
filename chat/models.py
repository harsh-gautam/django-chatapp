from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

AUTH_USER = settings.AUTH_USER_MODEL


class ChatRoom(models.Model):
    title = models.CharField(max_length=120, unique=True, blank=False)
    participants = models.ManyToManyField(AUTH_USER, help_text="users who are connected to chat room.")

    def __str__(self):
        return self.title

    def connect_user(self, user):
        is_connected = False
        if not user in self.participants.all():
            self.participants.add(user)
            is_connected = True
        elif user in self.participants.all():
            is_connected = True
        return is_connected

    def disconnect_user(self, user):
        is_disconnected = False
        if user in self.participants.all():
            self.participants.remove(user)
            is_disconnected = True
        return is_disconnected

    @property
    def group_name(self):
        return f"chatroom-{self.id}"

class ChatRoomMessage(models.Model):
    user = models.ForeignKey(AUTH_USER, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    content = models.TextField(unique=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:20] + " by " + self.user.username

    def get_room_messages(self, room):
        qs = ChatRoomMessage.objects.filter(room=room).order_by("-timestamp")
        return qs

    