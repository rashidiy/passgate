from rest_framework import viewsets

from devices.models import Event
from devices.serializers import EventSerializer


class EventModelViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    swagger_tags = ['Events']
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Event.objects.none()
        return Event.objects.filter(device_id=self.kwargs['device_pk'])
