from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
import requests

from ..models import Chat, Message
from ..serializers import ChatSerializer
from ..service import stt, tts
from rag.retrive import input_prompt


class CreateChatAPIView(APIView):
    parser_classes = [MultiPartParser] # Required for file uploads

    @extend_schema(
        summary="Start a new chat",
        description="Uploads an audio file, transcribes it, and generates an AI response.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'clinic': {'type': 'string'},
                    'audio': {'type': 'string', 'format': 'binary'}
                },
                'required': ['clinic', 'audio']
            }
        },
        responses={201: ChatSerializer}
    )
    def post(self, request):
        clinic = request.data.get("clinic")
        audio = request.FILES.get("audio")

        if not clinic or not audio:
            return Response(
                {"error": "clinic and audio are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        chat = Chat.objects.create(clinic=clinic)

        user_text = stt(audio)
        user_text = user_text.get("result", {}).get("conversation_text", "")[11:]

        user_message = Message.objects.create(
            chat=chat,
            text=user_text,
            is_user=True
        )
        user_message.audio.save(audio.name, audio)
        user_message.save()

        bot_text = input_prompt(user_text)

        bot_audio = tts(bot_text)
        audio_url = bot_audio.get("result", {}).get("url")

        if audio_url:
            # 2. Download the audio file bytes
            response = requests.get(audio_url)
            if response.status_code == 200:
                bot_audio_bytes = response.content

        bot_message = Message.objects.create(
            chat=chat,
            text=bot_text,
            is_user=False
        )
        if bot_audio_bytes:
            bot_message.audio.save(
                f"bot_{bot_message.id}.wav",
                ContentFile(bot_audio_bytes)
            )
        bot_message.save()

        return Response(
            {
                "answer": {
                    "id": chat.id,
                    "text": bot_text,
                    "audio": bot_message.audio.url
                }
            },
            status=status.HTTP_201_CREATED
        )


class AddMessageAPIView(APIView):
    @extend_schema(
        summary="Start a new chat",
        description="Uploads an audio file, transcribes it, and generates an AI response.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'audio': {'type': 'string', 'format': 'binary'}
                },
                'required': ['clinic', 'audio']
            }
        },
        responses={201: ChatSerializer}
    )
    def post(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response(
                {"error": "Chat not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        audio = request.FILES.get("audio")
        if not audio:
            return Response(
                {"error": "audio is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_text = stt(audio)
        user_text = user_text.get("result", {}).get("conversation_text", "")[11:]


        user_message = Message.objects.create(
            chat=chat,
            text=user_text,
            is_user=True
        )
        user_message.audio.save(audio.name, audio)
        user_message.save()

        bot_text = input_prompt(user_text)

        bot_audio = tts(bot_text)
        audio_url = bot_audio.get("result", {}).get("url")

        if audio_url:
            # 2. Download the audio file bytes
            response = requests.get(audio_url)
            if response.status_code == 200:
                bot_audio_bytes = response.content

        bot_message = Message.objects.create(
            chat=chat,
            text=bot_text,
            is_user=False
        )
        if bot_audio_bytes:
            bot_message.audio.save(
                f"bot_{bot_message.id}.wav",
                ContentFile(bot_audio_bytes)
            )
        bot_message.save()

        return Response(
            {
                "user_text": user_text,
                "answer": {
                    "text": bot_text,
                    "audio": bot_message.audio.url
                }
            },
            status=status.HTTP_201_CREATED
        )
