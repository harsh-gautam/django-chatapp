from django.shortcuts import render, redirect, Http404
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from chat.utils import find_room_or_error

# Create your views here.
def index(request):
    return render(request, 'index.html')

# Room view
@login_required(login_url='/')
def room(request, room_name):
    return render(request, 'chat/room.html', {'room_name': room_name, 'username': request.user.username})

# @login_required(login_url='/')
# def joinroom(request):
#     room_get = request.GET['join']
#     room = find_room_or_error(room_get)
#     if room is not None:
#         room(request, room.room_name)
#     else:
#         return Http404("ROOM NOT FOUND")




