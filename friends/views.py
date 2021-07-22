from django.shortcuts import render, HttpResponse
import json

from account.models import Account
from friends.models import FriendList, FriendRequest
from private_chat.models import PrivateChatRoom

def friend_list_view(request, *args, **kwargs):
    user = request.user
    context = {"error": ""}
    if user.is_authenticated:
        user_id = kwargs.get('user_id')
        if user_id:
            try:
                this_user = Account.objects.get(pk=user_id)
                context['this_user'] = this_user
            except Account.DoseNotExist:
                context['error'] = "User does not exists"
            
            try:
                this_user_friend_list = FriendList.objects.get(user=this_user)
            except:
                context['error'] = f"Could not find friend list of user {this_user.username}"

            # The authenticated user is not viewing his friend list
            friends = []
            if user != this_user:
                if user in this_user_friend_list.friends.all():
                    auth_user_friend_list = FriendList.objects.get(user=user)
                    
                    for friend in this_user_friend_list.friends.all():
                        if auth_user_friend_list.is_mutual_friend(friend):
                            friends.append(friend)
                    context['friends'] = friends
                else:
                    context['error'] = "You must be friends to  view friend list."
            else:
                for friend in this_user_friend_list.friends.all():
                    friends.append(friend)
                context["friends"] = friends

    else:
        context['error'] = "You must be authenticated to view others friend list."

    return render(request, "friends/friends_list.html", context)



# APIs
def send_friend_request(request, *args, **kwargs):

    user = request.user
    payload = {'response': None}
    if user.is_authenticated and request.method == "POST":
        # receiver_user_id = request.POST['receiver_user_id']
        print(request.body)
        receiver_user_id = json.loads(request.body)['receiver_user_id']

        if receiver_user_id:
            receiver = Account.objects.get(pk=receiver_user_id)
            try:
                friend_request = FriendRequest.objects.filter(sender=user, receiver=receiver, is_active=True)
                if friend_request:
                    payload['result'] = "error"
                    payload['response'] = "You already sent them friend request."
                else:
                    raise Exception()
            except Exception:
                friend_request = FriendRequest(sender=user, receiver=receiver)
                friend_request.save()
                payload['result'] = "success"
                payload['response'] = "Friend Request Sent"
            
            if payload['response'] == None:
                payload['result'] = "error"
                payload['response'] = "Something went wrong."
        else:
            payload['result'] = "error"
            payload['response'] = "Unable to send friend request"
    else:
        payload['result'] = "error"
        payload['response'] = "You must be authenticated to send friend request"

    return HttpResponse(json.dumps(payload), content_type="application/json")


def accept_friend_request(request):
    user = request.user
    payload = {"response": None}
    if user.is_authenticated and request.method == "GET":
        friend_req_id = request.GET['friend_req_id']
        if friend_req_id:
            try:
                friend_req = FriendRequest.objects.get(pk=friend_req_id)
                if friend_req:
                    friend_req.accept()
                    payload['result'] = "success"
                    payload['response'] = "Accepted friend request"
            except FriendRequest.DoesNotExist:
                payload['result'] = "error"
                payload['response'] = "Friend Request does not exists."

            if payload['response'] == None:
                payload['result'] = "error"
                payload['response'] = "Something went wrong"
        else:
            payload['result'] = "error"
            payload['response'] = "Something went wrong"
    else:
        payload['result'] = "error"
        payload['response'] = "You must be authenticated to accept friend requests."

    return HttpResponse(json.dumps(payload), content_type="application/json")

def cancel_friend_request(request):
    user = request.user
    payload = {"result": "error", "response": None}
    if user.is_authenticated and request.method == "GET":
        receiver_id = request.GET['receiver_id']
        if receiver_id:
            try:
                receiver_acc = Account.objects.get(pk=receiver_id)
                if receiver_acc:
                    try:
                        friend_req = FriendRequest.objects.filter(sender=user, receiver=receiver_acc, is_active=True)
                        if len(friend_req) > 1:
                            for req in friend_req:
                                req.cancel()
                        else:
                            friend_req.first().cancel()
                        payload['result'] = "success"
                        payload['response'] = "Cancelled Friend Request."
                    except FriendRequest.DoesNotExist:
                        payload['response'] = f"Cannot cancel request: {e}"
                else:
                    payload['response'] = "Something went wrong."
            except Account.DoesNotExist:
                payload['response'] = "Cannot find the user that."
        else:
            payload['response'] = "Something went wrong."
    else:
        payload['response'] = "You must be logged in to perform this action."

    return HttpResponse(json.dumps(payload), content_type="application/json")


def decline_friend_request(request):
    user = request.user
    payload = {"response": None}
    if user.is_authenticated and request.method == "GET":
        friend_req_id = request.GET['friend_req_id']
        if friend_req_id:
            try:
                friend_req = FriendRequest.objects.get(pk=friend_req_id)
                if friend_req:
                    friend_req.decline()
                    payload['result'] = "success"
                    payload['response'] = "Declined friend request"
            except FriendRequest.DoesNotExist:
                payload['result'] = "error"
                payload['response'] = "Friend Request does not exists."

            if payload['response'] == None:
                payload['result'] = "error"
                payload['response'] = "Something went wrong"
        else:
            payload['result'] = "error"
            payload['response'] = "Server Error"
    else:
        payload['result'] = "error"
        payload['response'] = "You must be authenticated to accept friend requests."

    return HttpResponse(json.dumps(payload), content_type="application/json")

def remove_friend(request):
    user = request.user
    payload = {"result": "error", "response": None}
    if user.is_authenticated and request.method == "GET":
        removee_id = request.GET['removee_id']
        if removee_id:
            try:
                removee_acc = Account.objects.get(pk=removee_id)
                if removee_acc:
                    try:
                        friend_list = FriendList.objects.get(user=user)
                        friend_list.unfriend(removee_acc)
                        payload['result'] = "success"
                        payload['response'] = f"Removed {removee_acc.username} from your friend list."
                    except Exception as e:
                        payload['response'] = f"Cannot remove friend: {e}"
                else:
                    payload['response'] = "Something went wrong while removing friend."
            except Account.DoesNotExist:
                payload['response'] = "Cannot find the user that you want to remove."
        else:
            payload['response'] = "Something went wrong."
    else:
        payload['response'] = "You must be logged in to perform this action."

    return HttpResponse(json.dumps(payload), content_type="application/json")