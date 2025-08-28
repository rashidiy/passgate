import time
from time import sleep

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from requests import Response, auth, ConnectTimeout, request
from rest_framework import exceptions as rex


class OrderManager:
    last_search_total = 0

    @classmethod
    def get_device(cls):
        from devices.models import Device
        try:
            return Device.objects.get(type=Device.DeviceTypes.ORDER)
        except Device.DoesNotExist:
            raise rex.ValidationError(detail=_("There is no order device."))

    @classmethod
    def get_url(cls, device, path):
        device = cls.get_device()
        return 'http://{}:{}{}'.format(device.ip_address, device.port, path)

    @classmethod
    def authenticate(cls, device):
        return auth.HTTPDigestAuth(device.username, device.password)

    @classmethod
    def switch_cam(cls, onoff: bool):
        path = '/ISAPI/AccessControl/CardReaderCfg/1'
        params = {'format': 'json'}
        data = {
            "CardReaderCfg": {
                "enable": onoff,
                "okLedPolarity": "anode",
                "errorLedPolarity": "anode",
                "swipeInterval": 0,
                "enableFailAlarm": False,
                "maxReadCardFailNum": 5,
                "pressTimeout": 10,
                "enableTamperCheck": True,
                "offlineCheckTime": 0,
                "fingerPrintCheckLevel": 5,
                "faceMatchThresholdN": 90,
                "faceRecogizeTimeOut": 3,
                "faceRecogizeInterval": 2,
                "cardReaderFunction": [
                    "fingerPrint",
                    "face"
                ],
                "cardReaderDescription": "DS-K1T343EFX",
                "livingBodyDetect": True,
                "faceMatchThreshold1": 90,
                "liveDetLevelSet": "general",
                "liveDetAntiAttackCntLimit": 100,
                "enableLiveDetAntiAttack": True,
                "fingerPrintCapacity": 3000,
                "fingerPrintNum": 1,
                "defaultVerifyMode": "faceOrFpOrCardOrPw",
                "faceRecogizeEnable": 1,
                "enableReverseCardNo": False,
                "independSwipeIntervals": 0,
                "maskFaceMatchThresholdN": 88,
                "maskFaceMatchThreshold1": 88
            }
        }
        device = cls.get_device()
        try:
            response = request(
                'PUT', cls.get_url(device, path), params=params, json=data, auth=cls.authenticate(device), timeout=5
            )
        except ConnectTimeout:
            raise ValidationError(_('Unable to connect to device with given IP and Port'))

        match response.status_code:
            case 401:
                raise ValidationError(_("Wrong username or password."))
            case 400:
                if response_json := response.json():
                    raise ValidationError(response_json.get('subStatusCode'))
            case 200:
                return response
        response.raise_for_status()

    @staticmethod
    def get_total_matches(response: Response) -> int:
        return response.json().get("AcsEvent").get("totalMatches")

    @classmethod
    def send_acs_request(cls, offset: int = 0, limit: int = 24):
        path = '/ISAPI/AccessControl/AcsEvent'
        params = {'format': 'json'}
        data = {
            "AcsEventCond": {
                "searchID": "0",
                "searchResultPosition": offset,
                "maxResults": limit,
                "major": 5,
                "minor": 0
            }
        }
        device = cls.get_device()
        try:
            response = request(
                'POST', cls.get_url(device, path), params=params, json=data, auth=cls.authenticate(device), timeout=5
            )
        except ConnectTimeout:
            raise ValidationError(_('Unable to connect to device with given IP and Port'))

        match response.status_code:
            case 401:
                raise ValidationError(_("Wrong username or password."))
            case 400:
                if response_json := response.json():
                    raise ValidationError(response_json.get('subStatusCode'))
            case 200:
                return response
        raise response.raise_for_status()

    @classmethod
    def get_last_search_total(cls) -> int:
        return cls.get_total_matches(cls.send_acs_request())

    @staticmethod
    def validate_minor(event_list):
        for event in event_list:
            if event.get('minor') in [75, 76, 1, 9]:
                return True
        return False

    @classmethod
    def check_face(cls, timeout=10):
        start_time = time.time()
        try:
            while True:
                response = cls.send_acs_request(cls.last_search_total)
                total_matches = cls.get_total_matches(response)

                if time.time() - start_time > timeout:
                    return 'timeout'

                if total_matches != cls.last_search_total:
                    cls.last_search_total = total_matches - 1
                    json_response = response.json()
                    info_list = json_response.get("AcsEvent").get("InfoList")
                    if info_list:
                        i = 1
                        while i < len(info_list):
                            info = info_list[-i]
                            minor = info.get("minor")
                            if minor in [76, 9]:
                                return 'unknown'
                            if minor in [75, 1]:
                                return info.get("employeeNoString")
                            i += 1
                sleep(1)
        except Exception:
            return 'error'
