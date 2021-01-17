from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from account.forms import RegistrationForm, LoginForm, UpdateForm
from account.models import Account

from friends.models import FriendRequest, FriendList
from friends.utils import FriendReqStatus, get_friend_req_or_false

# TODOs : implement image crop and upload image logic

def default_view(request):
    return redirect('home')

def register_view(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        return HttpResponse("You are already logged in.")

    context = {}
    
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email').lower()
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            destination = kwargs.get('next')
            if destination:
                return redirect(destination)
        else:
            context['registration_form'] = form

    return render(request, 'account/register.html', context)


def login_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        return redirect('home')

    context = {}
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            login(request, user)
            return redirect('home')
        else:
            context['login_form'] = form
    return render(request, 'account/login.html', context)

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')


def account_view(request, *args, **kwargs):
    """
    Logic for different states
        is_self(boolean) (is this your profile?)
            is_friend(boolean) (if not your profile then is this your friend?)
                1: Not a friend yet
                2: Other user sent you a friend request ( You recieved friend request)
                3: You send that user a friend request
    """
    context = {}
    user_id = kwargs.get('user_id')

    try:
        account = Account.objects.get(pk=user_id)
    except:
        return HttpResponse("User doesn't exists")

    if account:
        context['id'] = account.id
        context['username'] = account.username
        context['name'] = account.name
        context['email'] = account.email
        context['hide_email'] = account.hide_email
        context['profile_image'] = account.profile_image

        is_self = True
        is_friend = False
        
        try:
            friend_list = FriendList.objects.get(user=account)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=account)
            friend_list.save()
        friends = friend_list.friends.all()  # Get all the friends from user's friend list
        context["friends"] = friends

        user = request.user  # That's who is viewing page
        request_sent = 0
        friend_requests = None

        if user.is_authenticated and user != account:
            is_self = False

            if friends.filter(pk=user.id): # Is the viewer watching other user is in his/her friend list?
                is_friend = True

            else:
                is_friend = False
                
                # CASE 1: You send friend request
                if get_friend_req_or_false(user, account) != False:
                    request_sent = FriendReqStatus.YOU_SEND_REQUEST.value
                    
                # CASE 2: You recieved friend request
                elif get_friend_req_or_false(account, user) != False:
                    request_sent = FriendReqStatus.YOU_RECIEVED_REQUEST.value
                    context['pending_friend_req_id'] = get_friend_req_or_false(account, user).id
                    
                # CASE 3: No friend request send or recieved
                else:
                    request_sent = FriendReqStatus.NO_REQUEST_SEND_OR_RECIEVED.value
                    print("NO REQUEST: ", request_sent)

        elif not user.is_authenticated:
            is_self = False
        else:
            try:
                friend_requests = FriendRequest.objects.filter(reciever=user, is_active=True)
            except:
                pass

        context['is_self'] = is_self
        context['is_friend'] = is_friend
        context['friend_requests'] = friend_requests
        context['request_sent'] = request_sent
    print(type(context))
    print(context)
    return render(request, 'account/account.html', context)


def search_view(request, *args, **kwargs):
    context = {}
    search_query = request.GET['q']
    if len(search_query) > 0:
        search_results = Account.objects.filter(email__icontains=search_query).filter(username__icontains=search_query).filter(name__icontains=search_query).distinct()
        user = request.user
        accounts = []
        user_friends = []
        if user.is_authenticated:
            userAccount = Account.objects.get(username=user)
            user_friends = FriendList.objects.get(user=userAccount).friends.all()

        for account in search_results:
            if account in user_friends:
                accounts.append([account, True])
            else:
                accounts.append([account, False])

        context['accounts'] = accounts

    return render(request, "account/search_results.html", context)


def edit_account_view(request, *args, **kwargs):

    if not request.user.is_authenticated:
        return redirect('login')
    user_id = kwargs.get('user_id')
    try:
        account = Account.objects.get(pk=user_id)
    except:
        return HttpResponse("Something went wrong!")

    if account.pk != request.user.pk:
        return HttpResponse("You cannot edit someone else profile")
    context = {}
    if request.POST:
        form = UpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            print("VALID FORM")
            form.save()
            # new_username = form.cleaned_data['username']
            return redirect('account:profile', user_id=account.pk)
        else:
            print("INVALID FORM")
            form = UpdateForm(request.POST, instance=request.user,
				initial={
					"id": account.pk,
					"email": account.email, 
					"username": account.username,
                    "name": account.name,
					# "profile_image": account.profile_image,
					"hide_email": account.hide_email,
				}
			)
            context['form'] = form
    else:
        form = UpdateForm(
				initial={
					"id": account.pk,
					"email": account.email, 
					"username": account.username,
                    "name": account.name,
					# "profile_image": account.profile_image,
					"hide_email": account.hide_email,
				}
			)
        context['form'] = form
    # context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE  # Max image size in Bytes
    return render(request, "account/edit_account.html", context)