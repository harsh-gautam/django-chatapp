from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse

# Create your views here.
def index(request):
    return render(request, 'index.html')

# Room view
def room(request, room_name):
    return render(request, 'room.html', {'room_name': room_name})

def log_in(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse('index'))
        else:
            print(form.errors)
    return render(request, 'login.html', {'form': form})


def log_out(request):
    logout(request)
    return redirect(reverse('login'))

def sign_up(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('login'))
        else:
            print(form.errors)
    return render(request, 'signup.html', {'form': form})