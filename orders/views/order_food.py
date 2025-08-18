from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Employee, Order
from orders.views.base import get_face_result


class OrderFoodApi(APIView):
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
            try:
                employee = Employee.objects.get(id=face_result)
            except Employee.DoesNotExist:
                message = 'Shaxs tizimga kiritilmagan'
                return Response({'success': False, 'message': message})
            Order.objects.create(employee=employee, food_size=food_size)

            success_message = 'Buyurtma qabul qilindi!'
            return Response({'success': True, 'message': success_message})
