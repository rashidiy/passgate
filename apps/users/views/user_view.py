from rest_framework import viewsets, parsers

from users.models import User
from users.serializers import UserCreateSerializer, UserUpdateSerializer


class UserModelViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    swagger_tags = ['Users']
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserUpdateSerializer
