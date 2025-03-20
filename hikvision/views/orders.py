from datetime import datetime
from random import choice

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from hikvision.models import Order


class OrderList(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        timestamp_str = request.GET.get('timestamp')
        if not timestamp_str:
            return Response({"success": False, "message": "Missing timestamp"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except ValueError:
            return Response({"success": False, "message": "Invalid timestamp format"},
                            status=status.HTTP_400_BAD_REQUEST)

        now_ = timezone.now()
        if timestamp > now_:
            return Response({"success": False, "message": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        result = []
        for order in Order.objects.filter(updated_at__gt=timestamp):
            # for order in [Order.objects.first()]:
            result.append({
                "id": order.id,
                "employee_name": order.employee.name,
                "food_size": Order.FoodSizeChoice(order.food_size).label,
                "is_cancelled": order.is_cancelled,
                "created_at": Order.format_time(order.created_at),
                "updated_at": Order.format_time(order.updated_at),
                "user_type": order.employee.user_type.name,
                "is_created": (order.updated_at - order.created_at).total_seconds() < 5
            })
            print((order.updated_at - order.created_at).total_seconds())
        return Response({
            "success": True,
            "timestamp": now_.isoformat(),
            "result": result
        }, status=status.HTTP_200_OK)
