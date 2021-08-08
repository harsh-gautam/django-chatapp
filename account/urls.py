from django.urls import path
from account.views import (
    default_view,
    register_view,
    login_view,
    logout_view,
    account_view,
    edit_account_view,
    crop_image_view,
    )

app_name = "account"

urlpatterns = [
    path('', default_view, name='acccount_home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/<user_id>/', account_view, name="profile"),
    path('profile/<user_id>/edit/', edit_account_view, name="edit"),
    path('profile/<user_id>/edit/crop/', crop_image_view, name='crop-image'),
]
