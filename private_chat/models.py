from django.db import models
from django.conf import settings

AUTH_USER = settings.AUTH_USER_MODEL

# Create your models here.
class PrivateChatRoom(models.Model):
    user1 = models.ForeignKey(AUTH_USER, related_name="user1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(AUTH_USER, related_name="user2", on_delete=models.CASCADE)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user1.username}-{self.user2.username}"
    
    @property
    def group_name(self):
        return f"PrivateChatRoom-{self.pk}"
    

class PrivateChatMessage(models.Model):
    user = models.ForeignKey(AUTH_USER, on_delete=models.CASCADE)
    room = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE)
    content = models.TextField(blank=False, unique=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:15] + " by " + self.user.username