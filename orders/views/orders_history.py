import string
from datetime import timedelta, datetime, time
from random import choice

import pytz
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Employee, Order
from orders.utils.redis_manager import RedisManager
from orders.views.base import get_face_result
from root import settings

redis = RedisManager()


class GenerateToken(APIView):
    def get(self, request):
        face_result = get_face_result()
        if isinstance(face_result, Response):
            return face_result
        try:
            employee = Employee.objects.get(id=face_result)
        except Employee.DoesNotExist:
            message = 'Shaxs tizimga kiritilmagan'
            return Response({'success': False, 'message': message})
        token = ''.join([choice(string.ascii_letters + string.digits) for _ in range(32)])
        redis.set(f'token:{token}', employee.id, 180)
        return Response({
            'success': True, 'token': token, 'employee_name': employee.name, 'employee_profile': employee.face_image.url
        })


class GetRecentOrderList(APIView):
    def get(self, request):
        if not (token := request.GET.get('token')):
            return Response({'success': False, "message": "Missing \"token\""}, status.HTTP_400_BAD_REQUEST)
        if len(token) != 32:
            return Response({'success': False, "message": "Invalid \"token\""}, status.HTTP_400_BAD_REQUEST)

        employee_id = redis.get(f'token:{token}')

        if not employee_id:
            return Response({'success': False, "message": "Token expired"}, status.HTTP_403_FORBIDDEN)
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            message = 'Shaxs tizimga kiritilmagan'
            return Response({'success': False, 'message': message}, status.HTTP_503_SERVICE_UNAVAILABLE)

        today_start = datetime.combine(timezone.now().date(), time.min)
        utc_plus_5 = pytz.timezone('Asia/Tashkent')
        today_start_local = utc_plus_5.localize(today_start)
        today_start_utc = today_start_local.astimezone(pytz.UTC)
        orders = employee.orders.order_by('-created_at').filter(created_at__gt=today_start_utc)

        return Response({
            'success': True,
            'response': [
                {
                    "id": order.id,
                    "name": order.name,
                    "is_cancelled": order.is_cancelled,
                    "food_size": order.food_size,
                    "created_at": timezone.localtime(order.created_at, timezone=utc_plus_5)
                } for order in orders
            ]
        })


class CancelOrder(APIView):
    def get(self, request):
        if not (token := request.GET.get('token')):
            return Response({'success': False, "message": "Missing \"token\""}, status=status.HTTP_400_BAD_REQUEST)
        if len(token) != 32:
            return Response({'success': False, "message": "Invalid \"token\""}, status=status.HTTP_400_BAD_REQUEST)
        if not (order_id := request.GET.get('order_id')):
            return Response({'success': False, "message": "Missing \"order_id\""}, status=status.HTTP_400_BAD_REQUEST)

        employee_id = redis.get(f'token:{token}')
        if not employee_id:
            return Response({'success': False, "message": "Invalid or expired token"},
                            status=status.HTTP_401_UNAUTHORIZED)

        utc_plus_5 = pytz.timezone('Asia/Tashkent')
        now_local = timezone.localtime(timezone.now(), utc_plus_5)  # Current time in UTC+05:00

        restrict_begin_time = datetime.strptime(settings.CANCEL_RESTRICT_BEGIN, "%H:%M").time()  # 19:30
        restrict_end_time = datetime.strptime(settings.CANCEL_RESTRICT_END, "%H:%M").time()  # 10:00

        current_time = now_local.time()

        if restrict_begin_time > restrict_end_time:  # Overnight restriction (e.g., 19:30 to 10:00)
            is_restricted = (current_time >= restrict_begin_time or current_time < restrict_end_time)
        else:
            is_restricted = (restrict_begin_time <= current_time < restrict_end_time)

        if is_restricted:
            message = "Ayni vaqtda buyurtmalarni bekor qilib bo'lmaydi. Iltimos administratorga murojaat qiling!"
            return Response({'success': False, "message": message}, status=status.HTTP_403_FORBIDDEN)

        try:
            distance = timezone.now() - timedelta(minutes=10)
            order = Order.objects.get(id=order_id, employee_id=employee_id)
            if order.created_at < distance:
                message = 'Buyurtmani bekor qilish muddati tugagan. Iltimos administratorga murojaat qiling!'
                return Response({'success': False, 'message': message}, status=status.HTTP_403_FORBIDDEN)

            order.is_cancelled = True
            order.save()
            return Response({'success': True, "message": f"{order.id} raqamli buyurtma bekor qilindi"})
        except Order.DoesNotExist:
            return Response({'success': False, "message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
