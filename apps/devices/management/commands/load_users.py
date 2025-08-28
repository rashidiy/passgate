import asyncio
from getpass import getpass

import aiohttp
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from devices.plugins import DS_K1T671MF
from employees.models import Employee, Card


class Command(BaseCommand):
    user_count = 0
    session = aiohttp.ClientSession
    help = "Custom run command with username/password"

    def add_arguments(self, parser):
        parser.add_argument("address", type=str, help="Camera device address.")
        parser.add_argument("--username", type=str)
        parser.add_argument("--password", type=str)

    def handle(self, *args, **options):
        address = options.get("address")
        username = options.get('username') or input("Username: ")
        password = options.get('password') or getpass()
        asyncio.run(self.main(*address.split(':'), username, password))

    async def get_image(self, camera, image_url) -> ContentFile:
        image_path = image_url[image_url.index('/LOCALS/'):]
        image_byte = await camera.get_image(image_path)
        image_name = image_path[image_path.rindex('/') + 1: image_path.rindex('@')]
        return ContentFile(image_byte, image_name)

    async def get_cards(self, camera, employee_no: str) -> list[str]:
        path = '/ISAPI/AccessControl/CardInfo/Search'
        params = {'format': 'json'}
        data = {"CardInfoSearchCond": {
            "searchID": "1",
            "maxResults": 30,
            "searchResultPosition": 0,
            "EmployeeNoList": [
                {"employeeNo": employee_no}
            ]
        }}
        async with self.session.post(camera.url(path), params=params, json=data) as response:
            if response.status == 200 and response.content_type == 'application/json':
                rjson = await response.json()
                return [card['cardNo'] for card in rjson['CardInfoSearch']['CardInfo']]
        return []

    async def get_user(self, camera: DS_K1T671MF, user: dict):
        try:
            employee = Employee(
                name=user.get('name'), gender=user.get('gender')
            )
            if face_url := user.get('faceURL'):
                employee.image = await self.get_image(camera, face_url)
            await employee.asave()
            if user.get('numOfCard'):
                cards = await self.get_cards(camera, user.get('employeeNo'))
                await Card.objects.abulk_create((Card(card_no=card, employee=employee) for card in cards))
            print(f'User {employee.name} has been created with {user.get('numOfCard')} card(s).')
            self.user_count += 1
        except ValidationError as e:
            raise e
        except Exception as e:
            print(f'Error while creating user: {e}')

    async def main(self, ip, port, username, password):
        camera = DS_K1T671MF(ip_address=ip, port=port, username=username, password=password)
        await camera._check_model_match()
        self.stdout.write(self.style.SUCCESS(f"Successfully connected!"))
        middlewares = (aiohttp.DigestAuthMiddleware(username, password),)
        async with aiohttp.ClientSession(middlewares=middlewares) as session:
            self.session = session
            path = '/ISAPI/AccessControl/UserInfo/Search'
            params = {'format': 'json'}
            max_results = 30
            search_position = 0
            total_matches = 1
            while search_position <= total_matches:
                data = {
                    "UserInfoSearchCond": {
                        "searchID": "1", "maxResults": max_results, "searchResultPosition": search_position
                    }
                }
                async with session.post(camera.url(path), params=params, json=data) as response:
                    if response.status == 200 and response.content_type == 'application/json':
                        rjson = await response.json()
                        search_position += max_results
                        search_result = rjson.get('UserInfoSearch', {})
                        if tm := search_result.get('totalMatches'):
                            total_matches = tm
                        if users := search_result.get('UserInfo'):
                            await asyncio.gather(*[
                                self.get_user(camera, user) for user in users
                            ], return_exceptions=True)
                    await asyncio.sleep(1.2)
            print(f'{self.user_count} users have bee successfully created.')
