from django.db import models
from django.conf import settings

AUTH_USER = settings.AUTH_USER_MODEL

# Create your models here.
class PrivateChatRoom(models.Model):
    user1 = models.ForeignKey(AUTH_USER, related_name="user1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(AUTH_USER, related_name="user2", on_delete=models.CASCADE)
    connected_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="connected_users")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user1.username}-{self.user2.username}"
    
    def connect_user(self, user):
      is_user_added = False
      if not user in self.connected_users.all():
        self.connected_users.add(user)
        is_user_added = True
      return is_user_added

    def disconnect_user(self, user):
      """
      return true if user is removed from connected_users list
      """
      is_user_removed = False
      if user in self.connected_users.all():
        self.connected_users.remove(user)
        is_user_removed = True
      return is_user_removed

    @property
    def group_name(self):
        return f"PrivateChatRoom-{self.id}"


class PrivateChatMessageManager(models.Manager):
    def by_room(self, room):
        qs = PrivateChatMessage.objects.filter(room=room).order_by("-timestamp")
        return qs


class PrivateChatMessage(models.Model):
    user = models.ForeignKey(AUTH_USER, on_delete=models.CASCADE)
    room = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE)
    content = models.TextField(blank=False, unique=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = PrivateChatMessageManager()

    def __str__(self):
        return self.content[:15] + " by " + self.user.username