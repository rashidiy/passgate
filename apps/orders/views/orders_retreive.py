from rest_framework import viewsets

from orders.models import Order
from orders.serializers import OrderModelSerializer


class OrdersModelViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderModelSerializer
    swagger_tags = ['Orders']
    http_method_names = ['get', 'head', 'options']
