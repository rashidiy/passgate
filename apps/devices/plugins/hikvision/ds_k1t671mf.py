import asyncio
import xml.etree.ElementTree as ET
from datetime import timedelta

from django.core.exceptions import ValidationError, SynchronousOnlyOperation
from django.utils.translation import gettext_lazy as _

from devices.models import Device
from employees.models import AccessPoint, Card
from .base import HikvisionWebLogin


class DS_K1T671MF(HikvisionWebLogin):  # noqa
    device_model = Device.DeviceModels.DS_K1T671MF

    def check_model_match(self):
        return asyncio.run(self._check_model_match())

    def log_info(self, action, ap: AccessPoint):
        try:
            print(f'{action} [Device: {ap.device_id}; AccessPoint: {ap.id}] {ap.employee_id}:{ap.employee.name}')
        except SynchronousOnlyOperation:
            return

    async def _check_model_match(self):
        path = '/ISAPI/System/deviceInfo'
        response = await self.request('GET', path, timeout=5)
        ns = {'ns': 'http://www.isapi.org/ver20/XMLSchema'}
        root = ET.fromstring(response.text)
        model_value = root.find('ns:model', ns).text
        if model_value != self.device_model.label:
            raise ValidationError(_('Model is not %s.') % self.device_model)
        return True, self.device_model

    async def _record_user_data(self, method, path, access_device: AccessPoint):
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
        path = '/ISAPI/Intelligent/FDLib/FDSetUp'
        params = {'format': 'json'}
        with open(access_device.employee.image.path, 'rb') as image_file:
            data = {
                'FaceDataRecord': '{"faceLibType":"blackFD","FDID":"1","FPID":"%s"}' % access_device.employee.id,
                "img": image_file
            }
            await self.request('PUT', path, params=params, data=data, timeout=5)
            return True

    async def create_user(self, access_device: AccessPoint, replay_on_delete: bool = True):
        self.log_info('CreateUser', access_device)
        try:
            await self._record_user_data('POST', '/ISAPI/AccessControl/UserInfo/Record', access_device)
            if access_device.employee.image:
                await self._setup_face_id(access_device)
            return True
        except ValidationError as e:
            await self.delete_user(access_device)
            if replay_on_delete:
                await asyncio.sleep(2)
                return await self.create_user(access_device, False)
            raise e

    async def update_user(self, access_device: AccessPoint):
        self.log_info('ModifyUser', access_device)
        try:
            await self._record_user_data('PUT', '/ISAPI/AccessControl/UserInfo/Modify', access_device)
            if access_device.employee.image:
                await self._setup_face_id(access_device)
            return True
        except ValidationError as e:
            if 'employeeNoNotExist' in str(e):
                return await self.create_user(access_device)

    async def delete_user(self, access_device: AccessPoint):
        self.log_info('DeleteUser', access_device)
        path = '/ISAPI/AccessControl/UserInfo/Delete'
        params = {'format': 'json'}
        data = {"UserInfoDelCond": {"EmployeeNoList": [{"employeeNo": str(access_device.employee_id)}]}}
        await self.request('PUT', path, params=params, json=data, timeout=5)
        return True

    async def add_card(self, card: Card):
        path = '/ISAPI/AccessControl/CardInfo/Record'
        params = {'format': 'json'}
        data = {"CardInfo": {"employeeNo": str(card.employee_id), "cardNo": card.card_no, "cardType": "normalCard"}}
        await self.request('POST', path, params=params, json=data, timeout=5)
        return True

    async def remove_card(self, card: Card):
        path = '/ISAPI/AccessControl/CardInfo/Delete'
        params = {'format': 'json'}
        data = {"CardInfoDelCond": {"CardNoList": [{"cardNo": card.old_card}]}}
        re = await self.request('PUT', path, params=params, json=data, timeout=5)
        print(data)
        print(re.json)
        return True

    async def get_acs_events(self, device):
        path = '/ISAPI/AccessControl/AcsEvent'
        params = {'format': 'json'}
        data = {
            "AcsEventCond": {
                "searchID": "0",
                "searchResultPosition": 0,
                "maxResults": 30,
                "major": 5,
                "minor": 0,
                "startTime": (device.last_timestamp + timedelta(seconds=1)).isoformat(timespec="seconds"),
            }
        }
        response = await self.request('POST', path, params=params, json=data, timeout=5)
        return response

    async def get_image(self, path):
        params = {'token': self.get_token()}
        response = await self.request('GET', path, params=params, timeout=15)
        return response.content
