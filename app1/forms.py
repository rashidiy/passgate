from django import forms

from app1.models import Order


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
