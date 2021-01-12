from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    phone = models.IntegerField(default=0)
    online = models.IntegerField(default=0)

    # Custom Property
    @property
    def username(self):
        return self.user.username

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = UserProfile(user=instance)
        profile.save()


class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:10] + "... by " + self.author.username
    
    def get_last_10_messages():
        return Message.objects.order_by('-timestamp').all()[:10]