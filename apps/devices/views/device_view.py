from rest_framework import viewsets

from devices.models import Device
from devices.serializers import DeviceSerializer


class DeviceModelViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    swagger_tags = ['Devices']
    http_method_names = ['get', 'post', 'patch', 'delete']
