from django.db import models

from employees.models import Employee
from django.utils.translation import gettext_lazy as _


class WorkingHourException(models.Model):
    class ExceptionTypes(models.TextChoices):
        LaborLeave = 'labor', _('LaborLeave')
        UnpaidLeave = 'unpaid', _('UnpaidLeave')
        WorkingTrip = 'working_trip', _('WorkingTrip')

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('Employee'))
    exception_type = models.CharField(_('Exception Type'), max_length=255, choices=ExceptionTypes.choices)
    start_time = models.DateTimeField(_('Start Time'))
    end_time = models.DateTimeField(_('End Time'))

    class Meta:
        verbose_name = _('Exception')
        verbose_name_plural = _('Working Hours')
