from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<str:room_name>/', views.room, name='chatroom'),
]