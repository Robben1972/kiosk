from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Chat
from ..serializers import ChatSerializer

class ChatListAPIView(APIView):
    def get(self, request):
        chats = Chat.objects.all().order_by("-id")
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)


class ChatDetailAPIView(APIView):
    def get(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response(
                {"error": "Chat not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ChatSerializer(chat)
        return Response(serializer.data)
