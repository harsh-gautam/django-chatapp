from django.shortcuts import render, redirect, Http404, HttpResponse
from django.contrib.auth import authenticate, login, logout
from chat.utils import find_room_or_error

from account.models import Account

def index(request):
    return render(request, 'index.html')

def handle_login(request):
    try:
        if request.method == "POST":
            user = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=user, password=password)

            if user is not None:
                login(request, user)
            else:
                return HttpResponse("Wrong Credentials")
            return redirect('/')
    except Exception as e:
        return HttpResponse("Some Error Occurred")


def handle_logout(request):
    logout(request)
    return redirect('/')

def register(request):
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST.get('lname', '')
        name = fname + lname
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']

        user = Account.objects.create_user(email, username, password)
        user.name = name
        # user.last_name = lname
        user.save()
        return redirect('/')
    return render(request, 'signup.html')

def createroom(request):
    if request.method == "POST":
        room = request.POST['roomName']
        return redirect(f'/chat/room/{room}')
    return Http404("Page Not Found")


def joinroom(request):
    room_name = request.GET['join']
    room_exist = find_room_or_error(room_name)
    print(room_exist)
    if room_exist is not None:
        return redirect(f'/chat/room/{room_name}')
    else:
        return Http404("ROOM NOT FOUND")

