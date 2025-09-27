import asyncio

from django.core.management import BaseCommand

from devices.models import Device
from employees.models import Employee, AccessPoint
from utils import model_actions_receiver


class Command(BaseCommand):
    help = "no help text"

    async def sync(self):
        devices = [device async for device in Device.objects.all()]
        async for employee in Employee.objects.all():
            await asyncio.sleep(0.2)
            for device in devices:
                ap = None
                try:
                    ap, created = await AccessPoint.objects.aget_or_create(employee=employee, device=device)
                    if not created:
                        ap.employee = employee
                        await model_actions_receiver.access_point_post_save(None, ap, created)
                except Exception as e:
                    if ap:
                        print(f'[{device.id}:{ap.id}]', end=' ')
                    print(f'Error occurred while creating access point: {e}.')

    def handle(self, *args, **options):
        asyncio.run(self.sync())
