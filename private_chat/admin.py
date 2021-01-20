from django.contrib import admin

# Register your models here.
from private_chat.models import PrivateChatRoom, PrivateChatMessage

admin.site.register((PrivateChatRoom, PrivateChatMessage))