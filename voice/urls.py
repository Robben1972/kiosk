from django.urls import path
from .views import (
    CreateChatAPIView,
    AddMessageAPIView,
    ChatListAPIView,
    ChatDetailAPIView,
)

urlpatterns = [
    path("chats/", ChatListAPIView.as_view()),
    path("chats/<int:chat_id>/", ChatDetailAPIView.as_view()),
    path("chats/create/", CreateChatAPIView.as_view()),
    path("chats/<int:chat_id>/message/", AddMessageAPIView.as_view()),
]
