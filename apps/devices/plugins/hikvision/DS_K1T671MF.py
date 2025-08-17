import json
import xml.etree.ElementTree as ET
from mimetypes import guess_type

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from requests import request, ConnectTimeout

from users.models import AccessPoint
from .base import HikvisionWebLogin


class DS_K1T671MF(HikvisionWebLogin):  # noqa
    def check_model_match(self):
        path = '/ISAPI/System/deviceInfo'
        try:
            response = request('GET', self.url(path), auth=self.auth, timeout=5)
        except ConnectTimeout:
            raise ValidationError(_('Unable to connect to device with given IP and Port'))
        match response.status_code:
            case 401:
                raise ValidationError(_("Wrong username or password."))
            case 200:
                ns = {'ns': 'http://www.isapi.org/ver20/XMLSchema'}
                root = ET.fromstring(response.text)
                model_value = root.find('ns:model', ns).text
                if model_value != 'DS-K1T671MF':
                    raise ValidationError(_('Model is not DS-K1T671MF.'))
                return True
        response.raise_for_status()

    def _record_user_data(self, access_device: AccessPoint):
        print('user_data')
        path = '/ISAPI/AccessControl/UserInfo/Record'
        params = {'format': 'json'}
        data = {
            "UserInfo": {
                "employeeNo": "user%s" % access_device.user.id,
                "name": access_device.user.name,
                "userType": access_device.type,
                "doorRight": "1",
                "RightPlan": [{"doorNo": 1, "planTemplateNo": "1"}],
                "Valid": {
                    "enable": True,
                    "beginTime": access_device.validity_start.strftime("%Y-%m-%dT%H:%M:%S"),
                    "endTime": access_device.validity_end.strftime("%Y-%m-%dT%H:%M:%S"),
                    "timeType": "local"
                },
                "gender": access_device.user.gender,
                "localUIRight": False,
                "maxOpenDoorTime": access_device.visit_time,
                "userVerifyMode": ""
            }
        }
        try:
            response = request('POST', self.url(path), params=params, json=data, auth=self.auth, timeout=5)
        except ConnectTimeout:
            raise ValidationError(_('Unable to connect to device with given IP and Port'))
        match response.status_code:
            case 401:
                raise ValidationError(_("Wrong username or password."))
            case 400:
                if response_json := response.json():
                    raise ValidationError(_(response_json.get('subStatusCode')))
            case 200:
                return True
        response.raise_for_status()

    def _setup_face_id(self, access_device: AccessPoint):
        print('f_id')
        path = '/ISAPI/Intelligent/FDLib/FDSetUp'
        params = {'format': 'json'}
        data = {"faceLibType": "blackFD", "FDID": "1", "FPID": "user%s" % access_device.user.id}
        file_type = guess_type(access_device.user.image.path)
        file_name = access_device.user.image.name.split('/')[-1]
        files = {
            "FaceDataRecord": ("metadata.json", json.dumps(data), "application/json"),
            "img": (file_name, access_device.user.image.file.file, f"image/{file_type}"),
        }
        try:
            response = request('PUT', self.url(path), params=params, data=data, files=files, auth=self.auth)
        except ConnectTimeout:
            raise ValidationError(_('Unable to connect to device with given IP and Port'))

        match response.status_code:
            case 401:
                raise ValidationError(_("Wrong username or password."))
            case 400:
                if response_json := response.json():
                    raise ValidationError(_(response_json.get('subStatusCode')))
            case 200:
                return True
        response.raise_for_status()

    def create_user(self, access_device: AccessPoint):
        try:
            self._record_user_data(access_device)
            if access_device.user.image:
                self._setup_face_id(access_device)
        except ValidationError as e:
            self.delete_user(access_device)
            raise e

    def update_user(self, access_device: AccessPoint):
        ...

    def delete_user(self, access_device: AccessPoint):
        print('delete')
        path = '/ISAPI/AccessControl/UserInfo/Delete'
        params = {'format': 'json'}
        data = {"UserInfoDelCond": {"EmployeeNoList": [{"employeeNo": "user%s" % access_device.user.id}]}}
        try:
            response = request('PUT', self.url(path), params=params, json=data, auth=self.auth)
        except ConnectTimeout:
            raise ValidationError(_('Unable to connect to device with given IP and Port'))

        match response.status_code:
            case 401:
                raise ValidationError(_("Wrong username or password."))
            case 400:
                if response_json := response.json():
                    raise ValidationError(_(response_json.get('subStatusCode')))
            case 200:
                return True
        response.raise_for_status()
