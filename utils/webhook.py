import asyncio

import aiohttp

from devices import models as device_models
from devices import serializers as device_serializers
from employees import models as employee_models
from employees import serializers as employee_serializers


class WebhookManager:
    @classmethod
    async def get_data(cls, obj) -> dict:
        match obj.__class__:
            case device_models.Device:
                return device_serializers.DeviceSerializer(obj).data
            case employee_models.Employee:
                return employee_serializers.EmployeeCreateSerializer(obj).data
            case employee_models.Card:
                return employee_serializers.CardSerializer(obj).data
            case employee_models.AccessPoint:
                return employee_serializers.AccessPointSerializer(obj).data
            case device_models.Event:
                return device_serializers.EventSerializer(obj).data
        raise ValueError('Unsupported object type.')

    @classmethod
    async def send_update(cls, webhook: device_models.webhook, obj, type_):
        if webhook.is_active:
            async with aiohttp.ClientSession() as session:
                data = {
                    'type': type_,
                    'model': obj.__class__.__name__,
                    'data': await cls.get_data(obj)
                }
                async with session.post(webhook.url, json=data) as resp:
                    if (
                            resp.status == 200 and
                            resp.content_type == 'application/json' and
                            (await resp.json()) == {'success': True}
                    ):
                        return True
                webhook.is_active = False
                await webhook.asave()
                raise RuntimeError('Sending update to webhook failed for %s.' % webhook.url)

    @classmethod
    async def broadcast(cls, obj, type_):
        await asyncio.gather(
            *[cls.send_update(webhook, obj, type_) async for webhook in device_models.Webhook.objects.all()],
            return_exceptions=True
        )
