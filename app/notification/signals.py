from django.db.models.signals import post_save
from django.dispatch import receiver

from app.notification.models import Notification


@receiver(post_save, sender=Notification)
def send_notification_websocket(sender, instance, created, **kwargs):
    if created:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        notification_data = {
            "type": "new_notification",
            "id": instance.id,
            "user_id": instance.user.id,
            "notification_type": instance.type,
            "title": instance.title,
            "message": instance.message,
            "is_read": instance.is_read,
            "delivered_at": instance.delivered_at.isoformat() if instance.delivered_at else None,
            "created_at": instance.ctreated_at.isoformat(),
        }
        
        async_to_sync(channel_layer.group_send)(
            f"notifications_{instance.user.id}",
            {
                "type": "send_notification",
                "notification": notification_data
            }
        )
