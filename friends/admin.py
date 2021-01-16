from django.contrib import admin

from friends.models import FriendList, FriendRequest

admin.site.register((FriendList, FriendRequest))
