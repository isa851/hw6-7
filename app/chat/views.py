from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.chat.authentication import QueryParamJWTAuthentication
from app.chat.models import ChatRoom
from app.chat.serializers import (
    ChatRoomCreateSerializer,
    ChatRoomSerializer
)

token_parameter = openapi.Parameter(
    "token",
    openapi.IN_QUERY,
    description="JWT access token. Example : ?token=<token>",
    type=openapi.TYPE_STRING,
    required=True    
)

class ChatRoomViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    permission_classes = [IsAuthenticated]
    authentication_classes = [QueryParamJWTAuthentication]
    
    def get_queryset(self):
        return (
            ChatRoom.objects.filter(participants=self.request.user)
            .prefetch_related('participants', 'messages__sender')
            .select_related('created_by')
            .distinct()
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return ChatRoomCreateSerializer
        return ChatRoomSerializer

    @swagger_auto_schema(manual_parameters=[token_parameter])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        manual_parameters=[token_parameter],
        request_body=ChatRoomSerializer,
        responses={201: ChatRoomSerializer}
    )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat = serializer.save()
        return Response(ChatRoomSerializer(chat).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(manual_parameters=[token_parameter])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    