from django.contrib import admin
from chat.models import Message, Contact, ChatRoom

# Register your models here.
admin.site.register((Message, Contact, ChatRoom))

# @admin.register(UserProfile)
# class ProfileAdmin(admin.ModelAdmin):
 
#     list_display = ("username", "phone", "online")
 
#     search_fields = ["user__username"]