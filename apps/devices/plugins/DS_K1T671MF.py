import xml.etree.ElementTree as ET

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from requests import auth, request, ConnectTimeout


class DS_K1T671MF:  # noqa
    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.auth = auth.HTTPDigestAuth(username, password)

    def url(self, path):
        return 'http://{}:{}{}'.format(self.ip, self.port, path)

    def check_model_match(self):
        print('check start')
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
