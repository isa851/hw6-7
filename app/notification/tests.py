from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from django.test import override_settings
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from app.notification.models import Notification, NotificationType
from app.notification.tasks import deliver_notification
from app.notification.views import NotificationReadAPI
from app.users.models import User, UserRole
from core.asgi import application


TEST_CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}


@override_settings(CHANNEL_LAYERS=TEST_CHANNEL_LAYERS)
class NotificationWebSocketTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email="ws@example.com",
            password="testpass123",
            first_name="Web",
            last_name="Socket",
            role=UserRole.CUSTOMER,
        )
        self.token = str(AccessToken.for_user(self.user))

    async def _connect(self):
        communicator = WebsocketCommunicator(
            application,
            f"/ws/notifications/?token={self.token}",
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        return communicator

    def test_deliver_notification_sends_message_to_expected_group(self):
        async def scenario():
            communicator = await self._connect()
            notification = Notification.objects.create(
                user=self.user,
                type=NotificationType.ORDER_STATUS_CHANGED,
                title="Test notification",
                message="Order updated",
            )

            deliver_notification(notification.id)

            payload = await communicator.receive_json_from(timeout=1)
            self.assertEqual(payload["id"], notification.id)
            self.assertEqual(payload["type"], NotificationType.ORDER_STATUS_CHANGED)
            self.assertEqual(payload["message"], "Order updated")
            self.assertIsNotNone(payload["created_at"])
            await communicator.disconnect()

        async_to_sync(scenario)()

    def test_notification_read_api_sends_read_event(self):
        async def scenario():
            communicator = await self._connect()
            notification = Notification.objects.create(
                user=self.user,
                type=NotificationType.ORDER_STATUS_CHANGED,
                title="Read notification",
                message="Mark as read",
            )

            request = self.factory.patch(f"/api/v1/notification/notifications/{notification.id}/read")
            request.user = self.user
            response = NotificationReadAPI.as_view({"patch": "partial_update"})(request, pk=notification.id)

            self.assertEqual(response.status_code, 200)
            payload = await communicator.receive_json_from(timeout=1)
            self.assertEqual(payload, {"type": "notification_read", "id": notification.id, "is_read": True})
            await communicator.disconnect()

        async_to_sync(scenario)()
