import socket
from typing import Iterable

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from devices.models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type_badge", "model", "ip_address", "port", "username")
    list_display_links = ("id", "name")
    list_filter = ('type', 'model')
    search_fields = ("name", "ip_address", "username")
    ordering = ("type", "name")
    list_per_page = 20
    readonly_fields = ("model", "encrypted_password")
    fieldsets = (
        (_("General"), {
            "fields": ("name", "type", "model"),
        }),
        (_("Network"), {
            "fields": ("ip_address", "port"),
        }),
        (_("Credentials"), {
            "fields": ("username", "password_placeholder"),
        }),
    )

    actions = ("action_ping_socket",)

    @admin.display(description=_("Type"), ordering="type")
    def type_badge(self, obj: Device):
        color = "#16a34a" if obj.type == Device.DeviceTypes.ACCESS else "#2563eb"
        label = Device.DeviceTypes(obj.type).label
        return format_html(
            '<span style="display:inline-block;padding:.15rem .5rem;border-radius:.5rem;'
            'font-size:12px;font-weight:600;color:#fff;background:{};">{}</span>',
            color, label
        )

    def get_readonly_fields(self, request, obj: Device | None = None):
        ro = list(super().get_readonly_fields(request, obj))
        if obj:
            ro.extend(["ip_address", "port"])
        return tuple(ro)

    def save_model(self, request, obj: Device, form, change):
        try:
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, "; ".join(e.messages), level=messages.ERROR)
            raise

    @admin.action(description=_("Ping socket (IP:Port)"))
    def action_ping_socket(self, request, queryset: Iterable[Device]):
        timeout = 2.0
        ok, fail = 0, 0
        for device in queryset:
            try:
                with socket.create_connection((device.ip_address, device.port), timeout=timeout):
                    ok += 1
            except OSError as exc:
                fail += 1
                self.message_user(
                    request,
                    _("[{}] {} @ {}:{} not reachable: {}").format(
                        device.id, device.name, device.ip_address, device.port, exc
                    ),
                    level=messages.ERROR,
                )
        if ok:
            self.message_user(request, _("%d device(s) reachable.") % ok, level=messages.SUCCESS)
