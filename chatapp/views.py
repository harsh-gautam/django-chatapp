from django.shortcuts import render, redirect, Http404, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

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
        lname = request.POST['lname']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(username, email, password)
        user.first_name = fname
        user.last_name = lname
        user.save()
        return redirect('/')
    return render(request, 'signup.html')

def createroom(request):
    if request.method == "POST":
        room = request.POST['roomName']
        return redirect(f'/chat/room/{room}')
    return Http404("Page Not Found")