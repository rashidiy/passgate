from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils.translation import gettext_lazy as _


class ExportIntervalForm(forms.Form):
    start = forms.SplitDateTimeField(
        label=_("From"),
        required=True,
        widget=AdminSplitDateTime(),
        help_text=_("Start date and time"),
    )
    end = forms.SplitDateTimeField(
        label=_("To"),
        required=True,
        widget=AdminSplitDateTime(),
        help_text=_("End date and time"),
    )
    include_all_employees = forms.BooleanField(
        label=_("Include Employees Without Events"),
        required=False,
        initial=False,
    )

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start")
        end = cleaned.get("end")

        # Only validate if both are present
        if start and end:
            # Optional: normalize to your local tz if needed
            # start = _ensure_local_aware(start)
            # end = _ensure_local_aware(end)

            if end <= start:
                # Attach to the 'end' field for clear UX
                self.add_error("end", _("End must be after start."))

        return cleaned
