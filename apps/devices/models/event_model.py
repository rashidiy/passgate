"""
card
{
    "major": 5,
    "minor": 1,
    "time": "2025-08-24T18:04:37+05:00",
    "cardNo": "3308812528",
    "cardType": 1,
    "name": "HabibulloH Rashidov",
    "cardReaderNo": 1,
    "doorNo": 1,
    "employeeNoString": "31",
    "serialNo": 10455,
    "userType": "normal",
    "currentVerifyMode": "faceOrFpOrCardOrPw",
    "mask": "unknown"
},
{
    "major": 5,
    "minor": 9,
    "time": "2025-08-24T18:02:25+05:00",
    "cardNo": "3308812528",
    "cardType": 1,
    "cardReaderNo": 1,
    "doorNo": 1,
    "serialNo": 10450,
    "currentVerifyMode": "faceOrFpOrCardOrPw",
    "mask": "unknown"
},
face
{
    "major": 5,
    "minor": 75,
    "time": "2025-08-24T17:37:02+05:00",
    "cardType": 1,
    "name": "HabibulloH Rashidov",
    "cardReaderNo": 1,
    "doorNo": 1,
    "employeeNoString": "30",
    "serialNo": 10436,
    "userType": "normal",
    "currentVerifyMode": "faceOrFpOrCardOrPw",
    "mask": "no",
    "pictureURL": "http://192.168.88.226/LOCALS/pic/acsLinkCap/202508_00/24_173702_30075_0.jpeg@WEB000000000463",
    "FaceRect": {
        "height": 0.416,
        "width": 0.234,
        "x": 0.303,
        "y": 0.224
    }
},
{
    "major": 5,
    "minor": 76,
    "time": "2025-08-24T17:49:52+05:00",
    "cardType": 1,
    "cardReaderNo": 1,
    "doorNo": 1,
    "serialNo": 10442,
    "currentVerifyMode": "faceOrFpOrCardOrPw",
    "mask": "no",
    "pictureURL": "http://192.168.88.226/LOCALS/pic/acsLinkCap/202508_00/24_174952_30076_0.jpeg@WEB000000000464",
    "FaceRect": {
        "height": 0.501,
        "width": 0.282,
        "x": 0.298,
        "y": 0.227
    }
},
Fingerprint
{
    "major": 5,
    "minor": 38,
    "time": "2025-08-24T18:25:30+05:00",
    "cardNo": "3308812527",
    "cardType": 1,
    "name": "HabibulloH Rashidov",
    "cardReaderNo": 1,
    "doorNo": 1,
    "employeeNoString": "31",
    "serialNo": 10472,
    "userType": "normal",
    "currentVerifyMode": "faceOrFpOrCardOrPw",
    "mask": "unknown"
},
{
    "major": 5,
    "minor": 39,
    "time": "2025-08-24T18:12:37+05:00",
    "cardType": 1,
    "cardReaderNo": 1,
    "doorNo": 1,
    "serialNo": 10468,
    "currentVerifyMode": "faceOrFpOrCardOrPw",
    "mask": "unknown"
}

id, minor, time, [employee], [pictureURL], [cardNo], (serialNo), (currentVerifyMode)
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Event(models.Model):
    class EventTypes(models.TextChoices):
        MINOR_1 = 'valid_card', _('Authenticated via Card')
        MINOR_9 = 'invalid_card', _('Authentication via Card Failed')
        MINOR_75 = 'valid_face', _('Authenticated via Face')
        MINOR_76 = 'invalid_face', _('Authentication via Face Failed')
        MINOR_38 = 'valid_fingerprint', _('Authenticated via Fingerprint')
        MINOR_39 = 'invalid_fingerprint', _('Authentication via Fingerprint Failed')

    current_verify_mode = models.CharField(max_length=50, editable=False)
    serial_no = models.IntegerField(editable=False)
    type = models.CharField(max_length=20, choices=EventTypes)
    timestamp = models.DateTimeField()
    employee = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, related_name='events', null=True, blank=True)
    picture_url = models.ImageField(upload_to='events/pictures', null=True, blank=True)
    card_no = models.CharField(max_length=20, null=True, blank=True)
