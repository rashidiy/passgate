from rest_framework import serializers

from employees.models import AccessPoint


class AccessPointSerializer(serializers.ModelSerializer):
    visit_time = serializers.IntegerField(default=0)

    class Meta:
        model = AccessPoint
        exclude = ['employee']


class AccessPointUpdateSerializer(serializers.ModelSerializer):
    visit_time = serializers.IntegerField(default=0)

    class Meta:
        model = AccessPoint
        exclude = ['employee', 'device']
