import json

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def validate_image_size(value):
    max_size_kb = 200
    if value.size > max_size_kb * 1024:
        raise ValidationError(_('Image size shouldnt exteed %s Kb.') % max_size_kb)


class Employee(models.Model):
    class Genders(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        UNKNOWN = 'unknown', _('Unknown')

    name = models.CharField(_('Name'), max_length=100)
    gender = models.CharField(_('Gender'), max_length=7, choices=Genders.choices, default=Genders.MALE)
    image = models.ImageField(_('Image'), upload_to='users/', null=True, blank=True, validators=[validate_image_size])
    ex_data = models.TextField(editable=False)

    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')

    @property
    def data(self):
        return {
            'name': self.name,
            'gender': self.gender,
            'image': None if not self.image else self.image.url,
        }

    @property
    def old_data(self):
        if self.ex_data:
            return json.loads(self.ex_data)

    def save(self, *args, **kwargs):
        if self.data != self.old_data:
            self.ex_data = json.dumps(self.data)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name
