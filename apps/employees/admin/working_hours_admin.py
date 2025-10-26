from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone as djtz
from django.utils.translation import gettext_lazy as _

from employees.admin.forms import ExportIntervalForm
from employees.models import WorkingHourException
from utils.working_hours_export import export_working_hours_to_excel


def _ensure_local_aware(dt):
    """Return an aware datetime normalized to the project's default timezone."""
    tz = djtz.get_default_timezone()
    if djtz.is_naive(dt):
        return djtz.make_aware(dt, tz)
    return dt.astimezone(tz)


@admin.register(WorkingHourException)
class WorkingHourExceptionAdmin(admin.ModelAdmin):
    list_display = 'pk', 'employee', 'exception_type', 'start_time', 'end_time'
    change_list_template = 'custom_admin/working_hours.html'

    def get_urls(self):
        return [
            path(
                'export_to_excel/',
                self.admin_site.admin_view(self.export_to_excel_view),
                name='export_to_excel',
            ),
        ] + super().get_urls()

    def export_to_excel_view(self, request):
        if request.method == "POST":
            form = ExportIntervalForm(request.POST)
            if form.is_valid():
                start = _ensure_local_aware(form.cleaned_data["start"])
                end = _ensure_local_aware(form.cleaned_data["end"])
                include_all = form.cleaned_data.get("include_all_employees", False)
                return export_working_hours_to_excel(
                    start_dt=start,
                    end_dt=end,
                    include_all_employees=include_all
                )
        else:
            this_month = djtz.localtime(djtz.now()).replace(day=1)
            form = ExportIntervalForm(initial={
                "start": this_month.replace(hour=0, minute=0, second=0, microsecond=0),
                "end": this_month.replace(hour=23, minute=59, second=59) + relativedelta(months=1, days=-1),
                "include_all_employees": False,
            })

        context = dict(
            self.admin_site.each_context(request),
            title=_("Export Working Hours (Interval)"),
            opts=self.model._meta,
            form=form,
        )
        return TemplateResponse(
            request,
            "custom_admin/export_interval_form.html",
            context
        )
