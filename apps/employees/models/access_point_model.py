from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def default_validity_end():
    return timezone.now() + relativedelta(years=3)


class AccessPoint(models.Model):
    class AccessTypes(models.TextChoices):
        NORMAL = 'normal', _('Normal')
        VISITOR = 'visitor', _('Visitor')

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='access_points',
                                 verbose_name=_('Employee'))
    device = models.ForeignKey('devices.Device', on_delete=models.CASCADE, related_name='access_points',
                               verbose_name=_('Device'))
    type = models.CharField(_('Type'), max_length=7, choices=AccessTypes.choices, default=AccessTypes.NORMAL)
    validity_start = models.DateTimeField(_('Validity start'), default=timezone.now)
    validity_end = models.DateTimeField(_('Validity end'), default=default_validity_end)
    visit_time = models.IntegerField(_('Visit time'), validators=[MinValueValidator(0), MaxValueValidator(255)],
                                     default=0)

    def __str__(self):
        return self.device.name

    def clean(self):
        if self.type == self.AccessTypes.VISITOR and not self.visit_time:
            raise ValidationError({'visit_time': _('Visit time is required.')})
        return super().clean()

    class Meta:
        unique_together = ('employee', 'device')
        verbose_name = _('Access Point')
        verbose_name_plural = _('Access Points')
