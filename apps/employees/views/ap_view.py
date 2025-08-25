from django.core.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError as RestValidationError

from employees.models import AccessPoint
from employees.serializers import AccessPointSerializer, AccessPointUpdateSerializer


class AccessPointModelViewSet(viewsets.ModelViewSet):
    model = AccessPoint
    serializer_class = AccessPointSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    swagger_tags = ['AccessPoints']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return AccessPoint.objects.none()

        return AccessPoint.objects.filter(employee_id=self.kwargs['user_pk'])

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return AccessPointUpdateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        try:
            serializer.save(employee_id=self.kwargs['user_pk'])
        except ValidationError as e:
            raise RestValidationError(*e)

    def perform_update(self, serializer):
        try:
            super().perform_update(serializer)
        except ValidationError as e:
            raise RestValidationError(*e)
