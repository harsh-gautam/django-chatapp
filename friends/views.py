from django.shortcuts import render, HttpResponse
import json

from account.models import Account
from friends.models import FriendList, FriendRequest

def send_friend_request(request, *args, **kwargs):

    user = request.user
    payload = {'response': None}
    if user.is_authenticated and request.method == "POST":
        # reciever_user_id = request.POST['reciever_user_id']
        reciever_user_id = json.loads(request.body)['reciever_user_id']

        if reciever_user_id:
            reciever = Account.objects.get(pk=reciever_user_id)
            try:
                friend_request = FriendRequest.objects.filter(sender=user, reciever=reciever, is_active=True)
                if friend_request:
                    payload['result'] = "error"
                    payload['response'] = "You already sent them friend request."
                else:
                    raise Exception()
            except Exception:
                friend_request = FriendRequest(sender=user, reciever=reciever)
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


def accept_friend_request(request, *args, **kwargs):
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