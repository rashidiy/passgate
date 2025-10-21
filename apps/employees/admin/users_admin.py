from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from employees.models import Employee, Card, AccessPoint
from ._atomic_create import AtomicAdminModelOverride


class CardInline(admin.TabularInline):
    model = Card
    extra = 1
    max_num = 5



class AccessPointForm(forms.ModelForm):
    class Meta:
        model = AccessPoint
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['device'].disabled = True


class AccessPointInline(admin.StackedInline):
    model = AccessPoint
    form = AccessPointForm
    extra = 1


@admin.register(Employee)
class EmployeeAdmin(AtomicAdminModelOverride):
    list_display = list_display_links = 'id', 'name', 'image_tag'
    list_filter = search_fields = 'id', 'name'
    readonly_fields = ("image_tag",)

    inlines = [CardInline, AccessPointInline]

    @admin.display(description=_('Image'))
    def image_tag(self, obj):
        if obj.image:
            image_url = obj.image.url
        else:
            image_url = '/static/users/img.png'

        return format_html('<img src="{}" style="max-width: 150px; max-height: 100px; border-radius: 10px;'
                           ' box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);'
                           ' border: 1px solid #ddd; padding: 3px;" />'.format(image_url))
