from rest_framework import viewsets, mixins

from employees.models import Card
from employees.serializers import CardSerializer


class CardModelViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    http_method_names = ["get", "post", "delete", "head", "options"]
    serializer_class = CardSerializer
    swagger_tags = ['Employees']
    lookup_field = "card_no"
    lookup_url_kwarg = "card_no"
    lookup_value_regex = r"[^/]+"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Card.objects.none()
        return Card.objects.filter(employee_id=self.kwargs['user_pk'])

    def perform_create(self, serializer):
        serializer.save(employee_id=self.kwargs['user_pk'])
