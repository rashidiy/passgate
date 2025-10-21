from datetime import datetime, timedelta, timezone

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from encrypted_fields import EncryptedTextField

from devices.plugins import PluginMixin


class Device(models.Model, PluginMixin):
    class DeviceTypes(models.TextChoices):
        ENTER = 'access_in', _('Enter')
        EXIT = 'access_out', _('Exit')
        ORDER = 'order', _('Order')

    name = models.CharField(_('Name'), max_length=100)
    type = models.CharField(_('Type'), max_length=100, choices=DeviceTypes.choices)
    model = models.CharField(_('Model'), max_length=100, choices=PluginMixin.DeviceModels.choices)
    ip_address = models.GenericIPAddressField(_('IP'))
    port = models.IntegerField(_('Port'), validators=[MinValueValidator(0), MaxValueValidator(65535)])
    username = models.CharField(_('Username'), max_length=100)
    password_placeholder = models.CharField(_('Password'), max_length=16)
    encrypted_password = EncryptedTextField(editable=False)
    last_timestamp = models.DateTimeField(default=datetime(2025, 9, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=5))))

    __old_username = None
    __old_pwd_placeholder = None

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Device')
        verbose_name_plural = _('Devices')
        unique_together = ('ip_address', 'port')

    @property
    def password(self):
        return self.encrypted_password or self.password_placeholder

    def _get_old_values(self):
        if not (self.__old_pwd_placeholder and self.__old_username):
            old_values = Device.objects.filter(pk=self.pk).values_list('password_placeholder', 'username').first()
            if old_values:
                self.__old_pwd_placeholder, self.__old_username = old_values

    def check_model_type(self):
        device = self.plugin(self.ip_address, self.port, self.username, self.password_placeholder)
        try:
            device.check_model_match()
        except ValidationError as e:
            raise e

    def encrypt_password(self):
        self.encrypted_password = self.password_placeholder
        self.password_placeholder = f'{self.password_placeholder[:2]}{'*' * (len(self.password_placeholder) - 2)}'

    def clean(self):
        self._get_old_values()
        if not self.pk:
            self.check_model_type()
            self.encrypt_password()
        elif self.__old_pwd_placeholder != self.password_placeholder:
            self.check_model_type()
            self.encrypt_password()
        elif self.__old_username != self.username:
            self.check_model_type()
        return super().clean()

    def save(self, *args, **kwargs):
        if not self.pk and self.type == Device.DeviceTypes.ORDER and Device.objects.filter(
                type=Device.DeviceTypes.ORDER).exists():
            raise ValidationError(_('You cannot create order Device more than one. Contact administrator.'))

        super().save(*args, **kwargs)

        if self.type == Device.DeviceTypes.ORDER:
            from devices.plugins.hikvision import OrderManager
            OrderManager.switch_cam(False)
