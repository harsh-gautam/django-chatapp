from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

AUTH_USER = settings.AUTH_USER_MODEL
# Create your models here.

class Notification(models.Model):
  # Who will recieve notification
  target = models.ForeignKey(AUTH_USER, on_delete=models.CASCADE)
  # Who will create notification
  from_user = models.ForeignKey(AUTH_USER, on_delete=models.CASCADE, null=True, blank=True, related_name="from_user")

  redirect_url = models.URLField(max_length=500, null=True, unique=False, blank=True, help_text="The url to be visited when notification is clicked.")
  
  # Text in Notification, Example: Harsh sent you a friend request
  notify_text = models.CharField(max_length=255, unique=False, blank=True, null=True) 

  timestamp = models.DateTimeField(auto_now_add=True)
  read = models.BooleanField(default=False) # notification status : read/unread

  # GENERIC TYPE that can refer to FriendList, UnRead Messages, or any other type of "Notification"
  content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
  object_id = models.PositiveIntegerField()
  content_object = GenericForeignKey()

  def __str__(self) -> str:
      return self.notify_text
  
  def get_content_object_type(self):
    return str(self.content_object.get_cname)
