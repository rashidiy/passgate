from django.contrib import admin
from django.http import JsonResponse, HttpResponse
from django.template.response import TemplateResponse
from django.utils.html import format_html

from camera import create_user, delete_user
from .models import Employee, Order, UserType


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    search_fields = ['name']

    def image_tag(self, obj):
        return format_html('<img src="{}" style="max-width: 150px; max-height: 100px; border-radius: 10px;'
                           ' box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);'
                           ' border: 1px solid #ddd; padding: 3px;" />'.format(obj.face_image.url))

    image_tag.short_description = 'Image'
    list_display = ['id', 'name', 'image_tag']
    list_display_links = ['id', 'name', 'image_tag']

    def delete_model(self, request, obj):
        delete_user([obj.id])
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        delete_user([i.id for i in queryset])
        super().delete_queryset(request, queryset)

    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            print(create_user(obj.id, obj.name, obj.face_image, obj.rfid))


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['employee', 'food_size', 'time', 'get_user_type']
    search_fields = ['employee', 'food_size']

    def get_user_type(self, obj):
        return obj.employee.user_type.name if obj.employee else None

    get_user_type.short_description = 'User Type'

    def changelist_view(self, request, extra_context=None):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Sahifani render qilib, faqat kerakli qismni qaytarish
            response = TemplateResponse(request, self.change_list_template, self.get_extra_context(request))
            response.render()
            content = response.content.decode('utf-8')
            start = content.find('<div id="result_list">')
            end = content.find('</div>', start) + len('</div>')
            result_list_html = content[start:end]
            return JsonResponse({'html': result_list_html})

        return super().changelist_view(request, extra_context)
