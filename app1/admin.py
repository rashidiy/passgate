from django.contrib import admin
from django.utils.html import format_html

from camera import create_user, delete_user
from .models import Employee, Order


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    search_fields = ['name']

    def image_tag(self, obj):
        return format_html('<img src="{}" style="max-width:200px; max-height:150px"/>'.format(obj.face_image.url))

    image_tag.short_description = 'Image'
    list_display = ['id', 'name', 'image_tag']

    def delete_model(self, request, obj):
        delete_user([obj.id])
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        delete_user([i.id for i in queryset])
        super().delete_queryset(request, queryset)

    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            print(create_user(obj.id, obj.name, obj.face_image))


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['employee', 'food_size', 'time']
    search_fields = ['employee', 'food_size']
