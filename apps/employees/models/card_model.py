from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Card(models.Model):
    card_no = models.CharField(_('Card number'), max_length=20, unique=True)
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='cards',
                                 verbose_name=_('Employee'))
    old_card = models.CharField(_('Card number'), max_length=20, editable=False)

    class Meta:
        verbose_name = _('Card')
        verbose_name_plural = _('Cards')

    def get_cards_count(self):
        if self.employee.pk:
            return Card.objects.filter(employee=self.employee).count()
        return 0

    def clean(self):
        if not self.pk and self.get_cards_count() >= 5:
            raise ValidationError(_('Limit of cards exceeded for user %s.') % self.employee.name)
        return super().clean()
