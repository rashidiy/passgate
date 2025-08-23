from rest_framework import serializers

from employees.models import Card


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['card_no']
