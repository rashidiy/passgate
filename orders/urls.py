from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from orders.views import OrderFoodApi, GetRecentOrderList, OrderList
from orders.views.orders_history import GenerateToken, CancelOrder

urlpatterns = (
        [
            path('order/', OrderFoodApi.as_view(), name='order-api'),
            path('orders/all/', OrderList.as_view(), name='order-all'),
            path('get_token/', GenerateToken.as_view(), name='get-token'),
            path('orders/recently/', GetRecentOrderList.as_view(), name='order-recently'),
            path('orders/cancel/', CancelOrder.as_view(), name='order-cancel'),
        ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
