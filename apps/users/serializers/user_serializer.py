from rest_framework import serializers

from users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'gender', 'image']


class UserUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['id', 'name', 'gender', 'image']
