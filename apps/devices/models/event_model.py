from django.db import models
from django.utils.translation import gettext_lazy as _


class Event(models.Model):
    class EventTypes(models.TextChoices):
        MINOR_1 = 'valid_card', _('Authenticated via Card')
        MINOR_9 = 'invalid_card', _('Authentication via Card Failed')
        MINOR_75 = 'valid_face', _('Authenticated via Face')
        MINOR_76 = 'invalid_face', _('Authentication via Face Failed')
        MINOR_38 = 'valid_fingerprint', _('Authenticated via Fingerprint')
        MINOR_39 = 'invalid_fingerprint', _('Authentication via Fingerprint Failed')

    current_verify_mode = models.CharField(_('Current Verify Mode'), max_length=50, editable=False)
    serial_no = models.IntegerField(_('Serial Number'), editable=False)
    type = models.CharField(_('Event Type'), max_length=20, choices=EventTypes.choices)
    timestamp = models.DateTimeField(_('Timestamp'))
    device = models.ForeignKey('devices.Device', related_name='events', on_delete=models.SET_NULL, null=True,
                               verbose_name=_('Device'))
    employee = models.ForeignKey('employees.Employee', related_name='events', on_delete=models.SET_NULL, null=True,
                                 blank=True, verbose_name=_('Employee'))
    employee_no = models.CharField(_('Employee Number'), max_length=255, null=True, blank=True)
    employee_name = models.CharField(_('Employee Name'), max_length=255, null=True, blank=True)
    picture = models.ImageField(_('Picture'), upload_to='events/pictures', null=True, blank=True)
    card_no = models.CharField(_('Card Number'), max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
