from django.urls import path

from . import views

urlpatterns = [
    path('friends/', views.friend_list, name='friend_list'),
    path('friends/add/', views.add_friend, name='add_friend'),
    path('friends/<int:pk>/accept/', views.accept_friend, name='accept_friend'),
    path('friends/<int:pk>/decline/', views.decline_friend, name='decline_friend'),
    path('chat/<int:friendship_id>/', views.chat_room, name='chat_room'),
]
