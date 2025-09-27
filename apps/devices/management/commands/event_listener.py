import asyncio
import logging
from datetime import datetime

from django.core.files.base import ContentFile
from django.core.management import BaseCommand

from devices.models import Device, Event
from devices.plugins import DS_K1T671MF
from employees.models import Employee

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class AccessEvent:
    currentVerifyMode: str = None
    minor: int = None
    serialNo: int = None
    time: str = None
    pictureURL: str = None
    employeeNoString: str = None
    name: str = None
    cardNo: str = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


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
        try:
            plugin = DS_K1T671MF(device.ip_address, device.port, device.username, device.password)
            response = await plugin.get_acs_events(device)
            acs_event = response.json.get('AcsEvent')
            if acs_event.get('numOfMatches'):
                logging.info(f'Found {acs_event.get('numOfMatches')} events on device {device.id}.')
                max_time = None
                for event in acs_event.get('InfoList'):
                    try:
                        event = AccessEvent(**event)
                        max_time = event.time
                        if event.minor not in cls.event_types.keys():
                            continue
                        employee_exists = await Employee.objects.filter(id=event.employeeNoString).aexists()
                        if event.employeeNoString and not employee_exists:
                            continue
                        image = None
                        if event.minor in (75, 76):
                            image_path = event.pictureURL[event.pictureURL.index('/LOCALS/'):]
                            file_name = f"event_{event.serialNo}.jpg"
                            image_bytes = await plugin.get_image(image_path)
                            image = ContentFile(image_bytes, name=file_name)
                        await Event.objects.acreate(
                            current_verify_mode=event.currentVerifyMode,
                            serial_no=event.serialNo,
                            type=cls.event_types[event.minor],
                            timestamp=event.time,
                            device=device,
                            employee_id=event.employeeNoString,
                            employee_no=event.employeeNoString,
                            employee_name=event.name,
                            picture=image,
                            card_no=event.cardNo,
                        )
                    except Exception as _:
                        logging.exception("Error creating event.")
                else:
                    if max_time:
                        device.last_timestamp = datetime.strptime(max_time, "%Y-%m-%dT%H:%M:%S%z")
                        await device.asave()
        except Exception as _:
            logging.exception("Error while requesting events.")

    @classmethod
    async def main(cls):
        logging.info('Listening for device events started.')
        while True:
            tasks = [cls.listen(device) async for device in
                     Device.objects.filter(type__in=(Device.DeviceTypes.ENTER, Device.DeviceTypes.EXIT))]
            await asyncio.gather(*tasks)
            await asyncio.sleep(1.5)


class Command(BaseCommand):
    help = "Custom run command with username/password"

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(EventListener.main())
