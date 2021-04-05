from django.shortcuts import render, redirect, Http404, HttpResponse
from django.contrib.auth import authenticate, login, logout

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
            return redirect('home')
    except Exception as e:
        return HttpResponse("Some Error Occurred")


def handle_logout(request):
    logout(request)
    return redirect('home')

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
        return redirect('home')
    return render(request, 'signup.html')

