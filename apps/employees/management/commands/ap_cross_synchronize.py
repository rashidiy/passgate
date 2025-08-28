import asyncio

from django.core.management import BaseCommand

from devices.models import Device
from employees.models import Employee, AccessPoint


class Command(BaseCommand):
    help = "no help text"

    async def sync(self):
        async for employee in Employee.objects.all():
            await asyncio.sleep(0.2)
            async for device in Device.objects.all():
                try:
                    await AccessPoint.objects.acreate(employee=employee, device=device)
                except Exception as e:
                    print(f'Error occurred while creating access point: {e}.')

    def handle(self, *args, **options):
        asyncio.run(self.sync())
