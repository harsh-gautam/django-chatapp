from django.contrib import admin
from chat.models import UserProfile

# Register your models here.

@admin.register(UserProfile)
class ProfileAdmin(admin.ModelAdmin):
 
    list_display = ("username", "phone", "online")
 
    search_fields = ["user__username"]