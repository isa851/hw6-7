from rest_framework import serializers 
from app.notification.models import Notification

class NotificationSerializers(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source="ctreated_at", read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title',
            'message', "is_read", "delivered_at",
            'ctreated_at', 'created_at'
        ]
