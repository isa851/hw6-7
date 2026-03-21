import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from app.chat.middleware import QueryParamJWTAuthMiddleware
from app.chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from app.notification.routing import websocket_urlpatterns as notification_websocket_urlpatterns

websocket_urlpatterns = chat_websocket_urlpatterns + notification_websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": QueryParamJWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        ),
    }
)
