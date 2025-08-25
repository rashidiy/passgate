import asyncio

from django.core.files.base import ContentFile
from django.core.management import BaseCommand

from devices.models import Device, Event
from devices.plugins import DS_K1T671MF


class EventListener:
    event_types = {
        1: 'valid_card',
        9: 'invalid_card',
        75: 'valid_face',
        76: 'invalid_face',
        38: 'valid_fingerprint',
        39: 'invalid_fingerprint'
    }

    @classmethod
    async def listen(cls, device: Device):
        plugin = DS_K1T671MF(device.ip_address, device.port, device.username, device.password)
        response = await plugin.get_acs_events(device)
        acs_event = response.json.get('AcsEvent')
        device.last_event = device.last_event + acs_event.get('numOfMatches')
        if acs_event.get('numOfMatches'):
            print(f'Found: {acs_event.get('numOfMatches')} events')
            for event in acs_event.get('InfoList'):
                try:
                    if event.get('minor') not in cls.event_types.keys():
                        continue
                    image = None
                    if event.get('minor') in (75, 76):
                        image_path = event.get('pictureURL')[event.get('pictureURL').index('/LOCALS/'):]
                        file_name = f"event_{event.get('serialNo')}.jpg"
                        image_bytes = await plugin.get_image(image_path)
                        image = ContentFile(image_bytes, name=file_name)
                    await Event.objects.acreate(
                        current_verify_mode=event.get('currentVerifyMode'),
                        serial_no=event.get('serialNo'),
                        type=cls.event_types[event.get('minor')],
                        timestamp=event.get('time'),
                        device=device,
                        employee_id=event.get('employeeNoString'),
                        employee_no=event.get('employeeNoString'),
                        employee_name=event.get('name'),
                        picture=image,
                        card_no=event.get('cardNo'),
                    )
                except Exception as _:
                    continue
        await device.asave()

    @classmethod
    async def main(cls):
        print('Listening...')
        while True:
            tasks = [cls.listen(device) async for device in Device.objects.filter(type=Device.DeviceTypes.ACCESS)]
            await asyncio.gather(*tasks)
            await asyncio.sleep(1)


class Command(BaseCommand):
    help = "Custom run command with username/password"

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(EventListener.main())
