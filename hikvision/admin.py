import openpyxl
from django.contrib import admin
from django.http import JsonResponse, HttpResponse
from django.template.response import TemplateResponse
from django.utils.html import format_html

from hikvision.plugins.DS_K1T671MF.camera import create_user, delete_user, update_user
from .models import Employee, Order, UserType


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    search_fields = ['name']

    def image_tag(self, obj):
        return format_html('<img src="{}" style="max-width: 150px; max-height: 100px; border-radius: 10px;'
                           ' box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);'
                           ' border: 1px solid #ddd; padding: 3px;" />'.format(obj.face_image.url))

    image_tag.short_description = 'Image'
    list_display = ['id', 'name', 'image_tag', 'user_type']
    list_display_links = ['id', 'name', 'image_tag']
    list_filter = ['id', 'name', 'user_type']

    def delete_model(self, request, obj):
        delete_user([obj.id])
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        delete_user([i.id for i in queryset])
        super().delete_queryset(request, queryset)

    def save_model(self, request, obj: Employee, form, change):
        old_obj = Employee.objects.filter(id=obj.id).first()
        obj.save()
        if not change:
            print(create_user(obj.id, obj.name, obj.face_image, obj.rfid))
        else:
            print(old_obj.face_image == obj.face_image)
            if old_obj.face_image == obj.face_image:
                print(update_user(obj.id, obj.name))
            else:
                print(update_user(obj.id, obj.name, obj.face_image, obj.rfid))


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


def export_to_excel(modeladmin, request, queryset):
    # Create a workbook and select the active worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Orders"

    # Define the header row
    headers = ['Employee', 'Name', 'Food Size', 'Time', 'User Type']
    ws.append(headers)

    # Append data rows
    for order in queryset:
        employee = order.employee
        user_type = employee.user_type.name if employee else ''
        # Format time if needed (adjust strftime format as necessary)
        time_value = order.time.strftime('%Y-%m-%d %H:%M:%S') if order.time else ''
        ws.append([str(employee), order.name, order.food_size, time_value, user_type])

    # Create a response with the appropriate Excel header.
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=orders.xlsx'
    wb.save(response)
    return response


export_to_excel.short_description = "Export Selected Orders to Excel"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['employee', 'name', 'food_size', 'is_cancelled', 'created_at', 'updated_at', 'get_user_type']
    search_fields = ['employee', 'name', 'food_size']
    actions = [export_to_excel]
    change_list_template = 'custom_admin/orders.html'

    def get_user_type(self, obj):
        return obj.employee.user_type.name if obj.employee else None

    get_user_type.short_description = 'User Type'

    def get_readonly_fields(self, request, obj=None):
        if request.user.has_perm('hikvision.can_cancel_orders'):
            return ('created_at', 'updated_at')
        return ('created_at', 'updated_at', 'is_cancelled')
