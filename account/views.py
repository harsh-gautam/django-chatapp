from chatapp.settings import MEDIA_ROOT
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core import files
from django.conf import settings
from account.forms import RegistrationForm, LoginForm, UpdateForm
from account.models import Account

from friends.models import FriendRequest, FriendList
from friends.utils import FriendReqStatus, get_friend_req_or_false

from private_chat.models import PrivateChatRoom
from private_chat.utils import find_or_create_private_chat

import json
import os
import cv2
import base64

MEDIA_ROOT = settings.MEDIA_ROOT
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
                return redirect('account:login')
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
                2: Other user sent you a friend request ( You received friend request)
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
              friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
          except:
              pass

        context['is_self'] = is_self
        context['is_friend'] = is_friend
        context['friend_requests'] = friend_requests
        context['request_sent'] = request_sent
    return render(request, 'account/account.html', context)


def search_view(request, *args, **kwargs):
    context = {}
    search_query = request.GET['q'].lower()
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
    print(request.POST, request.FILES)
    if request.POST:
        form = UpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            account.profile_image.delete()
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
					"profile_image": account.profile_image,
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
					"profile_image": account.profile_image,
					"hide_email": account.hide_email,
				}
			)
        context['form'] = form
    # context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE  # Max image size in Bytes
    return render(request, "account/edit_account.html", context)

def save_temp_profile_image_from_base64String(imageString, user):
  INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
  try:
    print(MEDIA_ROOT)
    if not os.path.exists(f"{MEDIA_ROOT}/profile_images/{str(user.pk)}/temp"):
      os.mkdir(f"{MEDIA_ROOT}/profile_images/{str(user.pk)}/temp")
    url = os.path.join(MEDIA_ROOT + "/profile_images/" + str(user.pk) + "/temp/temp_profile.png")
    storage = FileSystemStorage(location=url)
    image = base64.b64decode(imageString)
    with storage.open('', 'wb+') as destination:
      destination.write(image)
      destination.close()
    return url
  except Exception as e:
    print(e)
    if(str(e) == INCORRECT_PADDING_EXCEPTION):
      imageString += "=" * ((4 - len(imageString) % 4) % 4)
      return save_temp_profile_image_from_base64String(imageString, user)
  return None

def crop_image_view(request, *args, **kwargs):
  user = request.user
  payload = {}
  if request.method == 'POST' and user.is_authenticated:
    try:
      # print(request.body)
      data = json.loads(request.body)
      imageString = data["image"]
      url = save_temp_profile_image_from_base64String(imageString, user)
      img = cv2.imread(url)
      cropX = int(float(str(data['cropX'])))
      cropY = int(float(str(data['cropY'])))
      cropWidth = int(float(str(data['cropWidth'])))
      cropHeight = int(float(str(data['cropHeight'])))
      if cropX < 0:
        cropX = 0
      if cropY < 0:
        cropY = 0

      crop_img = img[cropY:cropY+cropHeight, cropX:cropX+cropWidth]
      cv2.imwrite(url, crop_img)
      user.profile_image.delete()
      # Save the cropped image to user model
      user.profile_image.save("profile_image.png", files.File(open(url, 'rb')))
      user.save()

      payload["result"] = "success"
      payload["cropped_profile_image"] = user.profile_image.url
      os.remove(url)
    except Exception as e:
      print(e)
      payload["result"] = "error"
      payload["exception"] = str(e)
  return HttpResponse(json.dumps(payload), content_type="application/json")