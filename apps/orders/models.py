from django.db import models
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

from employees.models import Employee

class Order(models.Model):
    class FoodSizeChoice(models.TextChoices):
        SMALL = "0.5", _('Small')
        MEDIUM = "1", _('Medium')
        BIG = "1.5", _('Large')

    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='orders', verbose_name=_('Employee'))
    name = models.CharField(_('Name'), max_length=225)
    food_size = models.CharField(_('Food size'), max_length=3, choices=FoodSizeChoice.choices)
    is_cancelled = models.BooleanField(_('Is cancelled'), default=False)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.employee.name
        super().save(*args, **kwargs)

    @staticmethod
    def format_time(time):
        months_uz = {
            "January": _("January"),
            "February": _("February"),
            "March": _("March"),
            "April": _("April"),
            "May": _("May"),
            "June": _("June"),
            "July": _("July"),
            "August": _("August"),
            "September": _("September"),
            "October": _("October"),
            "November": _("November"),
            "December": _("December"),
            "year": _("Year"),
        }
        created_at = localtime(time)
        formatted_time = created_at.strftime("%d-%B, %Y year %H:%M")

        for en, uz in months_uz.items():
            formatted_time = formatted_time.replace(en, str(uz))

        return formatted_time

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        permissions = [
            ("can_cancel_orders", "Can cancel orders"),
        ]
