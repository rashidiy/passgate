from django.urls import include, path
from rest_framework.routers import DefaultRouter

from devices.views.device_view import DeviceViewSet

router = DefaultRouter()
router.register('devices', DeviceViewSet)

urlpatterns = [
    path('devices/', include(router.urls))
]
