import openpyxl
from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = 'user', 'name', 'food_size', 'is_cancelled', 'created_at', 'updated_at'
    search_fields = 'user', 'name', 'food_size'
    change_list_template = 'custom_admin/orders.html'

    @admin.action(description=_("Export Selected Orders to Excel"))
    def export_to_excel(self, model_admin, request, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Orders"

        headers = ['Employee', 'Name', 'Food Size', 'Time']
        ws.append(headers)

        for order in queryset:
            employee = order.user

            time_value = order.time.strftime('%Y-%m-%d %H:%M:%S') if order.time else ''
            ws.append([str(employee), order.name, order.food_size, time_value])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=orders.xlsx'
        wb.save(response)
        return response

    def get_readonly_fields(self, request, obj=None):
        if request.user.has_perm('orders.can_cancel_orders'):
            return 'created_at', 'updated_at'
        return 'created_at', 'updated_at', 'is_cancelled'
