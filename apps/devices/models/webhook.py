from django.db import models
from django.utils.translation import gettext_lazy as _


class Webhook(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    url = models.URLField(_('URL'))
    is_active = models.BooleanField(_('Is active'), default=True)

    class Meta:
        verbose_name = _('Webhook')
        verbose_name_plural = _('Webhooks')