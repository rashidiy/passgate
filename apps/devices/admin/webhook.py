from django.contrib import admin

from devices.models import Webhook


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
