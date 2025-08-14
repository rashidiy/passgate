from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from encrypted_fields import EncryptedTextField

from devices.plugins.DS_K1T671MF import DS_K1T671MF


class Device(models.Model):
    class DeviceModels(models.TextChoices):
        DS_K1T671MF = 'ds_k1t671mf', 'DS-K1T671MF'

    class DeviceTypes(models.TextChoices):
        ACCESS = 'access', _('Enter / Exit')
        ORDER = 'order', _('Order')

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=DeviceTypes.choices, default=DeviceTypes.ACCESS)
    model = models.CharField(max_length=100, choices=DeviceModels.choices, default=DeviceModels.DS_K1T671MF, editable=False)
    ip_address = models.GenericIPAddressField(_('IP'))
    port = models.IntegerField()
    username = models.CharField(max_length=100)
    password_placeholder = models.CharField(_('Password'), max_length=16)
    encrypted_password = EncryptedTextField(editable=False)

    __old_username = None
    __old_pwd_placeholder = None

    @property
    def password(self):
        return self.encrypted_password or self.password_placeholder

    def _get_old_values(self):
        if not (self.__old_pwd_placeholder and self.__old_username):
            old_values = Device.objects.filter(pk=self.pk).values_list('password_placeholder', 'username').first()
            self.__old_pwd_placeholder, self.__old_username = old_values

    def check_model_type(self):
        device = DS_K1T671MF(self.ip_address, self.port, self.username, self.password_placeholder)
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

