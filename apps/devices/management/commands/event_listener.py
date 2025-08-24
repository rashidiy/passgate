from django.core.management import BaseCommand

from devices.models import Device
from devices.plugins import DS_K1T671MF


class EventListener:
    async def listen(self, device: Device):
        plugin = DS_K1T671MF(device.ip_address, device.port, device.username, device.password)
        ...

    async def main(self):
        while True:
            for device in Device.objects.filter(type=Device.DeviceTypes.ACCESS):
                ...


class Command(BaseCommand):
    help = "Custom run command with username/password"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f"Command successfully executed!"))
