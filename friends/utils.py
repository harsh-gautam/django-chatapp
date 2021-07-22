from enum import Enum
from friends.models import FriendRequest

# Enum class to return constant values
class FriendReqStatus(Enum):
    NO_REQUEST_SEND_OR_RECIEVED = 1
    YOU_SEND_REQUEST = 2
    YOU_RECIEVED_REQUEST = 3
#-------------------------------------


# returns the FriendRequest Object if found else False
def get_friend_req_or_false(sender, receiver):
    try:
        return FriendRequest.objects.get(sender=sender, receiver=receiver, is_active=True)
    except FriendRequest.DoesNotExist:
        return False
# ----------------------------------------------------