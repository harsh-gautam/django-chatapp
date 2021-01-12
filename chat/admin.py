from django.contrib import admin
from chat.models import UserProfile, Message, Contact, Chat

# Register your models here.
admin.site.register((Message, Contact, Chat))

@admin.register(UserProfile)
class ProfileAdmin(admin.ModelAdmin):
 
    list_display = ("username", "phone", "online")
 
    search_fields = ["user__username"]