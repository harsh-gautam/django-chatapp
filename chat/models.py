from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

User = settings.AUTH_USER_MODEL

# Create your models here.
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
#     phone = models.IntegerField(default=0)
#     online = models.IntegerField(default=0)

#     # Custom Property
#     @property
#     def username(self):
#         return self.user.username

#     def __str__(self):
#         return self.user.username

# @receiver(post_save, sender=User)
# def create_profile_for_new_user(sender, created, instance, **kwargs):
#     if created:
#         profile = UserProfile(user=instance)
#         profile.save()


class Contact(models.Model):
    user = models.ForeignKey(User, related_name="contacts", on_delete=models.CASCADE)
    friends = models.ManyToManyField('self', blank=True,)

    def __str__(self):
        return self.user.username

class ChatRoom(models.Model):
    title = models.CharField(max_length=124, unique=True, blank=False)
    participants = models.ManyToManyField(User, related_name="chats", blank=True, null=False)
    # messages = models.ManyToManyField(Message, blank=True)

    def __str__(self):
        return self.title

    @property
    def group_name(self):
        return f"PublicChatRoom-{self.id}"


class MessageManager(models.Manager):
    def by_room(self, room):
        qs = Message.objects.filter(room=room).order_by("-timestamp")
        return qs

class Message(models.Model):
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = MessageManager()

    def __str__(self):
        return self.content[:20] + "... by " + self.user.username
