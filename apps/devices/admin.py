from django.contrib import admin
from django.core.exceptions import ValidationError

from devices.models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name', 'password'
    readonly_fields = 'ip_address', 'port', 'model'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return []

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            print(e)
