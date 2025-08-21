from rest_framework import serializers

from users.models import AccessPoint


class AccessPointSerializer(serializers.ModelSerializer):
    visit_time = serializers.IntegerField(default=0)

    class Meta:
        model = AccessPoint
        exclude = ['user']


class AccessPointUpdateSerializer(serializers.ModelSerializer):
    visit_time = serializers.IntegerField(default=0)

    class Meta:
        model = AccessPoint
        exclude = ['user', 'device']
