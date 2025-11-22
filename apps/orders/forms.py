from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.forms import SplitDateTimeField
from django.utils.translation import gettext_lazy as _


class OrderForm(forms.Form):
    OPTIONS = [
        ('0.5', 'Kichik 0.5'),
        ('1.0', 'Normal 1.0'),
        ('1.5', 'Katta 1.5'),
    ]
    food_size = forms.ChoiceField(
        choices=OPTIONS,
        # widget=forms.Select(attrs={'class': 'form-select'}),
        # error_messages={'required': "Food size is not selected"}
        widget=forms.RadioSelect
    )


class ExportOrdersIntervalForm(forms.Form):
    start = SplitDateTimeField(
        label=_("Start"),
        widget=AdminSplitDateTime(),
        help_text=_("Select the start of the orders interval."),
    )

    end = SplitDateTimeField(
        label=_("End"),
        widget=AdminSplitDateTime(),
        help_text=_("Select the end of the orders interval."),
    )

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start")
        end = cleaned.get("end")

        if start and end and start > end:
            raise forms.ValidationError(
                _("The start date cannot be later than the end date.")
            )

        return cleaned
