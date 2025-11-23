from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils import timezone as djtz
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from utils.orders_export import _ensure_local_aware, export_orders_to_excel
from .forms import ExportOrdersIntervalForm
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'employee_link', 'name', 'food_size', 'is_cancelled', 'employee_image_column', 'created_at',
    )
    search_fields = 'employee', 'name', 'food_size'
    change_list_template = 'custom_admin/orders.html'
    actions = ("export_to_excel",)
    ordering = ('-created_at',)

    @admin.display(ordering='employee', description=_('Employee'))
    def employee_link(self, obj):
        if obj.employee_id:
            url = reverse("admin:employees_employee_change", args=[obj.employee_id])
            return format_html('<a href="{}">{}</a>', url, obj.employee)
        return "-"

    @admin.display(description=_('Photo'))
    def employee_image_column(self, obj):
        if obj.employee and obj.employee.image:
            return format_html(
                '''
                <div class="employee-image-cell" data-image-url="{url}">
                    <img src="{url}" alt="{name}"
                         style="max-width:60px;max-height:60px;border-radius:4px;">
                    <i class="fas fa-eye employee-eye" style="cursor:pointer;margin-left:8px;"></i>
                </div>
                ''',
                url=obj.employee.image.url,
                name=obj.employee.name,
            )
        return "-"

    def _order_device_exists(self):  # noqa
        from devices.models import Device
        return Device.objects.filter(type=Device.DeviceTypes.ORDER).exists()  # noqa

    def get_model_perms(self, request):
        if not self._order_device_exists():
            return {}
        return super().get_model_perms(request)

    def has_view_permission(self, request, obj=None):
        if not self._order_device_exists():
            return False
        return super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        if not self._order_device_exists():
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if not self._order_device_exists():
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not self._order_device_exists():
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if request.user.has_perm('orders.can_cancel_orders'):
            return 'created_at', 'updated_at'
        return 'created_at', 'updated_at', 'is_cancelled'

    def get_urls(self):
        return [
            path(
                'export_to_excel/',
                self.admin_site.admin_view(self.export_to_excel_view),
                name='orders_export_to_excel',
            ),
        ] + super().get_urls()

    def export_to_excel_view(self, request):
        if request.method == "POST":
            form = ExportOrdersIntervalForm(request.POST)
            if form.is_valid():
                start = _ensure_local_aware(form.cleaned_data["start"])
                end = _ensure_local_aware(form.cleaned_data["end"])
                return export_orders_to_excel(
                    start_dt=start,
                    end_dt=end,
                )
        else:
            now_local = djtz.localtime(djtz.now())
            this_month_start = now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            this_month_end = (this_month_start + relativedelta(months=1, days=-1)).replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

            form = ExportOrdersIntervalForm(initial={
                "start": this_month_start,
                "end": this_month_end,
                "include_all_employees": False,
            })

        context = dict(
            self.admin_site.each_context(request),
            title=_("Export Orders (Interval)"),
            opts=self.model._meta,
            form=form,
        )
        return TemplateResponse(
            request,
            "custom_admin/export_orders_form.html",
            context
        )
