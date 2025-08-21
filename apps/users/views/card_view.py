from rest_framework import viewsets, mixins

from users.models import Card
from users.serializers import CardSerializer


class CardModelViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    http_method_names = ["get", "post", "delete", "head", "options"]
    serializer_class = CardSerializer
    swagger_tags = ['Users']
    lookup_field = "card_no"
    lookup_url_kwarg = "card_no"
    lookup_value_regex = r"[^/]+"

    def get_queryset(self):
        return Card.objects.filter(user_id=self.kwargs['user_pk'])

    def perform_create(self, serializer):
        serializer.save(user_id=self.kwargs['user_pk'])
