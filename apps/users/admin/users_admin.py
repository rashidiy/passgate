from django.contrib import admin

from users.models import User, Card, AccessPoint
from ._atomic_create import AtomicAdminModelOverride


class CardInline(admin.TabularInline):
    model = Card
    extra = 1
    max_num = 5


class AccessPointInline(admin.StackedInline):
    model = AccessPoint
    extra = 1


@admin.register(User)
class UserAdmin(AtomicAdminModelOverride):
    list_display = 'pk', 'name'
    inlines = [CardInline, AccessPointInline]
