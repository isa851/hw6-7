try:
    from channels.layers import get_channel_layer
except ImportError:
    try:
        from channels_redis.core import RedisChannelLayer

        def get_channel_layer():
            return RedisChannelLayer()
    except ImportError:
        # Fallback - disable notifications if channels not available
        def get_channel_layer():
            return None

from asgiref.sync import async_to_sync
from celery import shared_task
from django.utils import timezone

from app.notification.models import Notification

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def deliver_notification(self, notification_id: int) -> None:
    notif = Notification.objects.filter(id=notification_id).first()

    if not notif:
        return

    if notif.delivered_at:
        return

    notif.delivered_at = timezone.now()
    notif.save(update_fields=["delivered_at"])

    channel_layer = get_channel_layer()
    if channel_layer is None:
        # Channel layer not available, skip WebSocket delivery
        return

    async_to_sync(channel_layer.group_send)(
        f"notifications_{notif.user_id}",
        {
            "type": "send_notification",
            "data": {
                "id": notif.id,
                "title": notif.title,
                "message": notif.message,
                "type": notif.type,
                "is_read": notif.is_read,
                "delivered_at": notif.delivered_at.isoformat() if notif.delivered_at else None,
                "created_at": notif.ctreated_at.isoformat(),
            }
        }
    )
