from django.contrib import admin

from devices.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'type', 'timestamp', 'device', 'employee', 'employee_no', 'employee_name', 'picture', 'card_no'
    )
    list_filter = ('type', 'timestamp', 'device', 'employee', 'employee_no', 'employee_name', 'card_no')
    search_fields = ('id', 'type', 'timestamp', 'employee_no', 'employee_name', 'card_no')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
