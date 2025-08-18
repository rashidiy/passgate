import json

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def validate_image_size(value):
    max_size_kb = 200
    if value.size > max_size_kb * 1024:
        raise ValidationError(_('Image size shouldnt exteed %s Kb.') % max_size_kb)


class User(models.Model):
    class Genders(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        UNKNOWN = 'unknown', _('Unknown')

    name = models.CharField(_('Name'), max_length=100)
    gender = models.CharField(max_length=7, choices=Genders.choices, default=Genders.MALE)
    image = models.ImageField(upload_to='users', null=True, blank=True, validators=[validate_image_size])
    ex_data = models.TextField(editable=False)

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
            if self.pk:
                for access_point in self.access_points.all():
                    access_point_post_save(User, access_point, False)
            super().save(*args, **kwargs)


class Card(models.Model):
    card_no = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_cards_count(self):
        return Card.objects.filter(user=self.user).count()

    def save(self, *args, **kwargs):
        if self.get_cards_count() >= 5:
            raise ValidationError(_('Limit of cards exceeded for user %s.') % self.user.name)
        if self.pk:
            card_post_delete(Card, Card.objects.get(pk=self.pk))
        card_post_save(Card, self, not self.pk)
        super().save(*args, **kwargs)


def default_validity_end():
    return timezone.now() + relativedelta(years=3)


class AccessPoint(models.Model):
    class AccessTypes(models.TextChoices):
        NORMAL = 'normal', _('Normal')
        VISITOR = 'visitor', _('Visitor')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_points')
    device = models.ForeignKey('devices.Device', on_delete=models.CASCADE, related_name='access_points')
    type = models.CharField(max_length=7, choices=AccessTypes.choices, default=AccessTypes.NORMAL)
    validity_start = models.DateTimeField(default=timezone.now)
    validity_end = models.DateTimeField(default=default_validity_end)
    visit_time = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(255)], default=0)

    def clean(self):
        if self.type == self.AccessTypes.VISITOR and not self.visit_time:
            raise ValidationError({'visit_time': _('Visit time is required.')})
        return super().clean()

    class Meta:
        unique_together = ('user', 'device')


@receiver(post_save, sender=AccessPoint)
def access_point_post_save(sender, instance: AccessPoint, created: bool, **kwargs):
    from devices.plugins import DS_K1T671MF

    camera = DS_K1T671MF(
        instance.device.ip_address, instance.device.port, instance.device.username, instance.device.password
    )

    if created:
        camera.create_user(instance)
    else:
        camera.update_user(instance)


@receiver(post_delete, sender=AccessPoint)
def access_point_post_delete(sender, instance: AccessPoint, **kwargs):
    from devices.plugins import DS_K1T671MF

    DS_K1T671MF(
        instance.device.ip_address, instance.device.port, instance.device.username, instance.device.password
    ).delete_user(instance)


def card_post_save(sender, instance: Card, created: bool, **kwargs):
    from devices.plugins import DS_K1T671MF
    for access_point in instance.user.access_points.all():
        DS_K1T671MF(
            access_point.device.ip_address, access_point.device.port,
            access_point.device.username, access_point.device.password
        ).add_card(instance)


@receiver(post_delete, sender=Card)
def card_post_delete(sender, instance: Card, **kwargs):
    from devices.plugins import DS_K1T671MF
    for access_point in instance.user.access_points.all():
        DS_K1T671MF(
            access_point.device.ip_address, access_point.device.port,
            access_point.device.username, access_point.device.password
        ).remove_card(instance)
