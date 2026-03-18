from django.urls import re_path

from app.chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"^wa/chat/rooms/(?P<chat_id>\d+)/$", ChatConsumer.as_asgi()),
]