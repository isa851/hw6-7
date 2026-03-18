from rest_framework.routers import DefaultRouter
from app.chat.views import ChatRoomViewSet

router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='rooms')

urlpatterns = router.urls