from rest_framework import serializers

from orders.models import Order


class OrderSerializer(serializers.Serializer):
    food_size = serializers.ChoiceField(choices=Order.FoodSizeChoice)
