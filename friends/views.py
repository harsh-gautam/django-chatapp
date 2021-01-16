from django.shortcuts import render, HttpResponse
import json

from account.models import Account
from friends.models import FriendList, FriendRequest

# Create your views here.
