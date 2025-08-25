import xml.etree.ElementTree as ET

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from employees.models import AccessPoint, Card
from .base import HikvisionWebLogin


class DS_K1T671MF(HikvisionWebLogin):  # noqa
    async def check_model_match(self):
        path = '/ISAPI/System/deviceInfo'
        response = await self.request('GET', path, timeout=5)
        ns = {'ns': 'http://www.isapi.org/ver20/XMLSchema'}
        root = ET.fromstring(await response.text())
        model_value = root.find('ns:model', ns).text
        if model_value != 'DS-K1T671MF':
            raise ValidationError(_('Model is not DS-K1T671MF.'))
        return True

    async def _record_user_data(self, method, path, access_device: AccessPoint):
        print('user_data')
        params = {'format': 'json'}
        data = {
            "UserInfo": {
                "employeeNo": str(access_device.employee.id),
                "name": access_device.employee.name,
                "userType": access_device.type,
                "doorRight": "1",
                "RightPlan": [{"doorNo": 1, "planTemplateNo": "1"}],
                "Valid": {
                    "enable": True,
                    "beginTime": access_device.validity_start.strftime("%Y-%m-%dT%H:%M:%S"),
                    "endTime": access_device.validity_end.strftime("%Y-%m-%dT%H:%M:%S"),
                    "timeType": "local"
                },
                "gender": access_device.employee.gender,
                "localUIRight": False,
                "maxOpenDoorTime": access_device.visit_time,
                "userVerifyMode": ""
            }
        }
        await self.request(method, path, params=params, json=data, timeout=5)
        return True

    async def _setup_face_id(self, access_device: AccessPoint):
        print('f_id')
        path = '/ISAPI/Intelligent/FDLib/FDSetUp'
        params = {'format': 'json'}
        with open(access_device.employee.image.path, 'rb') as image_file:
            data = {
                'FaceDataRecord': '{"faceLibType":"blackFD","FDID":"1","FPID":"%s"}' % access_device.employee.id,
                "img": image_file
            }
            await self.request('PUT', path, params=params, data=data, timeout=5)
            return True

    async def create_user(self, access_device: AccessPoint):
        try:
            await self._record_user_data('POST', '/ISAPI/AccessControl/UserInfo/Record', access_device)
            if access_device.employee.image:
                await self._setup_face_id(access_device)
        except ValidationError as e:
            await self.delete_user(access_device)
            raise e

    async def update_user(self, access_device: AccessPoint):
        await self._record_user_data('PUT', '/ISAPI/AccessControl/UserInfo/Modify', access_device)
        if access_device.employee.image:
            await self._setup_face_id(access_device)

    async def delete_user(self, access_device: AccessPoint):
        print('delete user')
        path = '/ISAPI/AccessControl/UserInfo/Delete'
        params = {'format': 'json'}
        data = {"UserInfoDelCond": {"EmployeeNoList": [{"employeeNo": str(access_device.employee_id)}]}}
        await self.request('PUT', path, params=params, json=data, timeout=5)
        return True

    async def add_card(self, card: Card):
        print('add_card')
        path = '/ISAPI/AccessControl/CardInfo/Record'
        params = {'format': 'json'}
        data = {"CardInfo": {"employeeNo": str(card.employee_id), "cardNo": card.card_no, "cardType": "normalCard"}}
        await self.request('POST', path, params=params, json=data, timeout=5)
        print('add_card_finish')
        return True

    async def remove_card(self, card: Card):
        print('remove_card')
        path = '/ISAPI/AccessControl/CardInfo/Delete'
        params = {'format': 'json'}
        data = {"CardInfoDelCond": {"CardNoList": [{"cardNo": card.card_no}]}}
        await self.request('PUT', path, params=params, json=data, timeout=5)
        print('remove_card_finish')
        return True

    async def get_acs_events(self, device):
        path = '/ISAPI/AccessControl/AcsEvent'
        params = {'format': 'json'}
        data = {
            "AcsEventCond": {
                "searchID": "0",
                "searchResultPosition": device.last_event,
                "maxResults": 30,
                "major": 5,
                "minor": 0
            }
        }
        response = await self.request('POST', path, params=params, json=data, timeout=5)
        return response

    async def get_image(self, path):
        params = {'token': self.get_token()}
        response = await self.request('GET', path, params=params, timeout=15)
        return response.content
