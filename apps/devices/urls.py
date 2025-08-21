from django.urls import include, path
from rest_framework.routers import DefaultRouter

from devices.views.device_view import DeviceModelViewSet

router = DefaultRouter()
router.register('device', DeviceModelViewSet)

urlpatterns = [
    path('', include(router.urls))
]
