import asyncio

from asgiref.sync import sync_to_async
from django.core.exceptions import SynchronousOnlyOperation
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from devices.models import Device, Event, Webhook
from employees.models import AccessPoint, Card, Employee
from utils.webhook import WebhookManager


@sync_to_async()
def get_plugin(instance: AccessPoint):
    from devices.plugins import DS_K1T671MF
    return DS_K1T671MF(
        instance.device.ip_address, instance.device.port, instance.device.username, instance.device.password
    )


async def __employee_post_save(instance, created):
    if not created:
        await asyncio.gather(*[
            __access_point_post_save(access_point, False) async for access_point in instance.access_points.all()
        ])


async def __access_point_post_save(instance: AccessPoint, created: bool):
    plugin = await get_plugin(instance)

    if created:
        await plugin.create_user(instance)
        await asyncio.gather(*[plugin.add_card(card) async for card in instance.employee.cards.all()])
    else:
        await plugin.update_user(instance)


async def __access_point_post_delete(instance: AccessPoint):
    plugin = await get_plugin(instance)
    await plugin.delete_user(instance)


async def __card_post_save(card: Card, access_point: AccessPoint):
    plugin = await get_plugin(access_point)
    await plugin.add_card(card)


async def __card_post_delete(card: Card, access_point: AccessPoint):
    plugin = await get_plugin(access_point)
    await plugin.remove_card(card)


async def webhook_save(instance, created: bool):
    await asyncio.create_task(WebhookManager.broadcast(instance, 'create' if created else 'update'))


async def webhook_delete(instance):
    await asyncio.create_task(WebhookManager.broadcast(instance, 'delete'))


@receiver(post_save, sender=Employee)
async def employee_post_save(sender, instance, created, **kwargs):
    await webhook_save(instance, created)
    await __employee_post_save(instance, created)


@receiver(post_delete, sender=Employee)
async def employee_post_delete(sender, instance, **kwargs):
    await webhook_delete(instance)


@receiver(post_save, sender=AccessPoint)
async def access_point_post_save(sender, instance: AccessPoint, created: bool, **kwargs):
    await webhook_save(instance, created)
    await __access_point_post_save(instance, created)


@receiver(post_delete, sender=AccessPoint)
async def access_point_post_delete(sender, instance: AccessPoint, **kwargs):
    await webhook_delete(instance)
    await __access_point_post_delete(instance)


@receiver(post_save, sender=Card)
async def card_post_save(sender, instance: Card, created: bool, **kwargs):
    await webhook_save(instance, created)
    if not created:
        await card_post_delete(sender, instance, **kwargs)
    await asyncio.gather(*[
        __card_post_save(instance, access_point)
        async for access_point in instance.employee.access_points.all()
    ])


@receiver(post_delete, sender=Card)
async def card_post_delete(sender, instance: Card, **kwargs):
    await webhook_delete(instance)
    try:
        await asyncio.gather(*[
            __card_post_delete(instance, access_point)
            async for access_point in instance.employee.access_points.all()
        ])
    except SynchronousOnlyOperation:
        pass


@receiver(post_save, sender=Device)
async def device_post_save(sender, instance: Device, created: bool, **kwargs):
    await webhook_save(instance, created)


@receiver(post_delete, sender=Device)
async def device_post_delete(sender, instance: Device, **kwargs):
    await webhook_delete(instance)


@receiver(post_save, sender=Event)
async def event_post_save(sender, instance: Event, created: bool, **kwargs):
    await webhook_save(instance, created)


@receiver(post_delete, sender=Event)
async def event_post_delete(sender, instance: Event, **kwargs):
    await webhook_delete(instance)
