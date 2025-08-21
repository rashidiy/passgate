from rest_framework import serializers

from orders.models import Order


class OrderModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
