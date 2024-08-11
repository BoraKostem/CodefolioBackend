from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Chat
import uuid
from users.models import MyUser
from django.utils import timezone
from rest_framework import status
from langchain_core.messages import AIMessage, HumanMessage
from backend.utils import ResponseFormatter
from .llm_communication import chat
import pickle
class ChatView(APIView):
    def post(self, request, *args, **kwargs):
        uuid1 = request.data.get("uuid")
        if not uuid1:
            user_id = request.data.get("user_id")
            if not user_id:
                return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="user_id or uuid is required.")
            uuid1 = str(uuid.uuid4())
            user = MyUser.objects.filter(id=user_id).first()
            Chat.objects.create(uuid=uuid1, user_id=user_id, user_name=user.name)
            user_id=user_id
            user_name=user.name
        else:
            chat_instance = Chat.objects.filter(uuid=uuid1).first()
            if not chat_instance:
                return ResponseFormatter.format_response(None, http_code=status.HTTP_404_NOT_FOUND, message="Chat not found.")
            chat_instance.last_activity = timezone.now()
            chat_instance.save()
            user_name = chat_instance.user_name
            user_id = chat_instance.user_id

        input = request.data.get("input")
        if not input:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="input is required.")
        response = chat(chat_uuid=uuid1, person_name=user_name, user_id=user_id, input_message=input)

        return ResponseFormatter.format_response({"response": response, "uuid": uuid1}, http_code=status.HTTP_200_OK, message="Success")
    def get(self, request, *args, **kwargs):
        uuid1 = request.query_params.get("uuid")
        if not uuid1:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="uuid is required.")
        chat_instance = Chat.objects.filter(uuid=uuid1).first()
        if not chat_instance:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_404_NOT_FOUND, message="Chat not found.")
        chat_instance.last_activity = timezone.now()
        chat_instance.save()
        try:
            with open(f"{uuid1}.pkl", 'rb') as chatfile:
                chat = pickle.load(chatfile)
        except IOError:
            chat = []
        return ResponseFormatter.format_response({"chat": chat, "uuid": uuid1}, http_code=status.HTTP_200_OK, message="Success")