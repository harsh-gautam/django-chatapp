from django.shortcuts import render, redirect, Http404, HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from chat.models import ChatRoom
from account.models import Account

# Create your views here.
def index(request):
    return render(request, 'index.html')

# Room view
@login_required(login_url='account:login')
def room(request, *args, **kwargs):
    room_title = kwargs.get('room_title')
    return render(request, 'chat/room.html', {'room_title': room_title })


def create_room(request):
    user = request.user
    if user.is_authenticated and request.method == "POST":
        room_title = request.POST['roomName']
        user_account = Account.objects.get(pk=user.id)
        try:
            room = ChatRoom.objects.get(title=room_title)
            if room:
                return HttpResponse("Room already exists join the room.")
        except ChatRoom.DoesNotExist:
            room = ChatRoom(title=room_title)
            room.save()
        return redirect('chat:room', room_title=room.title)
    else:
        return HttpResponse("You must be logged in to create room.")
          
            
def join_room(request):
    user = request.user
    if user.is_authenticated and request.method == "GET":
        room_title = request.GET['join']
        try:
            room = ChatRoom.objects.get(title=room_title)
            if room:
                return redirect("chat:room", room_title=room.title)
        except:
            return HttpResponse("Room does not exists.")
    else:
        return HttpResponse("You must be logged in to join a room.")

# @login_required(login_url='/')
# def joinroom(request):
#     room_get = request.GET['join']
#     room = find_room_or_error(room_get)
#     if room is not None:
#         room(request, room.room_name)
#     else:
#         return Http404("ROOM NOT FOUND")




