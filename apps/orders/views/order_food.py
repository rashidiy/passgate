from datetime import timedelta

from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Employee, Order
from orders.views.base import get_face_result


class OrderFoodApi(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(auto_schema=None)  # noqa
    def get(self, request):
        food_size = request.GET.get('food_size')
        if not food_size:
            return Response({"success": False, "message": "missing food_size"}, status.HTTP_400_BAD_REQUEST)

        if food_size not in ['0.5', '1', '1.5']:
            return Response({"success": False, "message": "invalid food_size"}, status.HTTP_400_BAD_REQUEST)

        face_result = get_face_result()

        if isinstance(face_result, Response):
            return face_result

        if face_result:
            last_order = Order.objects.filter(employee_id=face_result, food_size=food_size).first()

            if last_order and (now_ := timezone.now()) - last_order.created_at < timedelta(hours=8):
                distance = ((last_order.created_at + timedelta(hours=8)) - now_).seconds
                hours = distance // 3600
                distance %= 3600
                minutes = distance // 60
                distance %= 60
                success_message = f'{hours} soat {minutes} minut dan keyin qayta urining.'
                return Response({'success': False, 'message': success_message})

            try:
                employee = Employee.objects.get(id=face_result)
            except Employee.DoesNotExist:
                message = 'Shaxs tizimga kiritilmagan'
                return Response({'success': False, 'message': message})
            Order.objects.create(employee=employee, food_size=food_size)

            success_message = 'Buyurtma qabul qilindi!'
            return Response({'success': True, 'message': success_message})
