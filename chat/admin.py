from django.contrib import admin
from chat.models import UserProfile, Message

# Register your models here.
admin.site.register(Message)

@admin.register(UserProfile)
class ProfileAdmin(admin.ModelAdmin):
 
    list_display = ("username", "phone", "online")
 
    search_fields = ["user__username"]