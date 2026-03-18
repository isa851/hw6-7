import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from app.notification.models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return
            
        self.group_name = f"notifications_{self.user.id}"
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        await self.send(
            text_data=json.dumps({
                "type": "connection_established",
                "user_id": self.user.id,
            })
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["notification"]))

    @sync_to_async
    def get_unread_notifications(self):
        notifications = Notification.objects.filter(
            user=self.user, 
            is_read=False
        ).order_by("-id")[:10]
        
        return [
            {
                "id": notif.id,
                "type": notif.type,
                "title": notif.title,
                "message": notif.message,
                "is_read": notif.is_read,
                "delivered_at": notif.delivered_at.isoformat() if notif.delivered_at else None,
                "created_at": notif.ctreated_at.isoformat(),
            }
            for notif in notifications
        ]
