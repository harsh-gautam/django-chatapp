from django.shortcuts import render, redirect

# Create your views here.
def private_chat_room_view(request, *args, **kwargs):
    user = request.user

    if not user.is_authenticated:
        return redirect("account:login")
    context = {}
    return render(request, "private_chat/private_room.html", context)