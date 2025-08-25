from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from devices.views.device_view import DeviceModelViewSet
from devices.views.event_view import EventModelViewSet

router = DefaultRouter()
router.register('device', DeviceModelViewSet)
nested_router = NestedDefaultRouter(router, 'device', lookup='device')
nested_router.register('event', EventModelViewSet)

urlpatterns = [*router.urls, *nested_router.urls]
