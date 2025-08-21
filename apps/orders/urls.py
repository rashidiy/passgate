from django.urls import path, include
from rest_framework.routers import DefaultRouter

from orders.views import OrderFoodApi, GetRecentOrderList, OrderList
from orders.views.orders_history import GenerateToken, CancelOrder
from orders.views.orders_retreive import OrdersModelViewSet

router = DefaultRouter()
router.register('order', OrdersModelViewSet)
urlpatterns = [
    path('order/', OrderFoodApi.as_view(), name='order-api'),
    path('orders/all/', OrderList.as_view(), name='order-all'),
    path('get_token/', GenerateToken.as_view(), name='get-token'),
    path('orders/recently/', GetRecentOrderList.as_view(), name='order-recently'),
    path('orders/cancel/', CancelOrder.as_view(), name='order-cancel'),
    path('api/v1/orders/', include(router.urls)),
]
