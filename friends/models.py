from django.db import models
from django.conf import settings

AUTH_USER_MODEL = settings.AUTH_USER_MODEL

class FriendList(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    friends = models.ManyToManyField(AUTH_USER_MODEL, related_name="friends", blank=True)

    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        """
        Add a friend
        params -> account : the user to add to friendlist
        """
        if not account in self.friends.all():
            self.friends.add(account)

    def remove_friend(self, account):
        """
        Remove a friend, helper for unfriend
        param -> account: the user to remove from friendlist
        """
        if account in self.friends.all():
            self.friends.remove(account)

    def unfriend(self, removee):
        """
        To unfriend someone we need to remove the removee from our friendlist and ourself from removee's friendlist
        param -> removee: the user to remove from friendlist
        """

        me = self  # the person who is removing 

        me.remove_friend(removee)

        # Remove myself from the removee's friendlist
        removee_friends_list = FriendList.objects.get(user=removee)
        removee_friends_list.remove_friend(me.user)

    def is_mutual_friend(self, friend):
        if friend in self.friends.all():
            return True
        return False


class FriendRequest(models.Model):
    """
    This model will store all friendrequests info and status
    A friendrequest has two main parts:
        SENDER: the person sending friend request
        RECIEVER: the person receiving friend request
    """

    sender = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender")
    reciever = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reciever")

    is_active = models.BooleanField(blank=False, null=False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.username

    def accept(self):
        """
        Accept a friend request and update both sender's and reciever's friendlist
        """
        reciever_friendList = FriendList.objects.get(user=self.reciever)
        if reciever_friendList:
            reciever_friendList.add_friend(self.sender)
            sender_friendList = FriendList.objects.get(user=self.sender)
            if sender_friendList:
                sender_friendList.add_friend(self.reciever)
                self.is_active = False
                self.save()
    
    def decline(self):
        """
        Decline a friend request -> from reciever's perpective
        """
        self.is_active = False
        self.save()

    def cancel(self):
        """
        cancel a friend request -> from sender's perpective
        """
        self.is_active = False
        self.save()