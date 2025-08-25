import hashlib
import json as jsonlib
import time
import xml.etree.ElementTree as ET

import aiohttp
import requests
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from requests import Response, ConnectTimeout


class ResponseWrapper:
    def __init__(self, response, text=None, json_data=None, raw=None, content=None):
        self.response = response
        self.text = text
        self.json = json_data
        self.raw = raw
        self.content = content


class Capabilities:
    session_id: str
    challenge: str
    iterations: int
    salt: str
    session_id_version: str
    is_irreversible: bool
    is_session_id_valid_long_term: bool

    def __init__(self, response) -> None:
        self.load_capabilities(response)

    def load_capabilities(self, caps: Response) -> None:
        root = ET.fromstring(caps.content)
        namespace = {'ns': root.tag.split('}')[0].strip('{')}
        self.session_id = root.findtext('.//ns:sessionID', namespaces=namespace)
        self.challenge = root.findtext('.//ns:challenge', namespaces=namespace)
        self.iterations = int(root.findtext('.//ns:iterations', default='1', namespaces=namespace))
        self.salt = root.findtext('.//ns:salt', namespaces=namespace)
        self.session_id_version = root.findtext('.//ns:sessionIDVersion', namespaces=namespace)
        self.is_irreversible = root.findtext('.//ns:isIrreversible', namespaces=namespace) == 'true'
        self.is_session_id_valid_long_term = root.findtext('.//ns:isSupportSessionTag', default='false',
                                                           namespaces=namespace) == 'true'


class HikvisionWebLogin:
    session = requests.Session()

    def __init__(self, ip_address, port, username, password):
        self.ip_address = ip_address
        self.port = port
        self.username = username
        self.password = password
        self.caps = self.get_capabilities()
        self.digest_auth = aiohttp.DigestAuthMiddleware(self.username, self.password)

    def url(self, path):
        return 'http://{}:{}{}'.format(self.ip_address, self.port, path)

    def get_capabilities(self) -> Capabilities | None:
        path = "/ISAPI/Security/sessionLogin/capabilities"
        try:
            response = self.session.get(self.url(path), params={'username': self.username}, timeout=5)
        except ConnectTimeout:
            raise ValidationError('Connection timed out')
        match response.status_code:
            case 200:
                return Capabilities(response)
            case 404:
                raise ValidationError(_('Wrong username.'))
        response.raise_for_status()

    @staticmethod
    def sha256(data):
        return hashlib.sha256(data.encode()).hexdigest()

    @classmethod
    def encode_password(cls, password, challenge, username, salt, iterations, is_irreversible):
        if is_irreversible:
            r = cls.sha256(username + salt + password)
            r = cls.sha256(r + challenge)
            for _ in range(2, iterations):
                r = cls.sha256(r)
        else:
            r = cls.sha256(password) + challenge
            for _ in range(1, iterations):
                r = cls.sha256(r)
        return r

    def get_login_data(self):
        return """
        <SessionLogin>
            <userName>{username}</userName>
            <password>{encoded_pass}</password>
            <sessionID>{session_id}</sessionID>
            <isSessionIDValidLongTerm>{session_id_valid_long_term}</isSessionIDValidLongTerm>
            <sessionIDVersion>{session_id_version}</sessionIDVersion>
            <isNeedSessionTag>true</isNeedSessionTag>
        </SessionLogin>
        """.format(
            username=self.username,
            encoded_pass=self.encode_password(
                self.password, self.caps.challenge, self.username, self.caps.salt,
                self.caps.iterations, self.caps.is_irreversible
            ),
            session_id=self.caps.session_id,
            session_id_valid_long_term=str(self.caps.is_session_id_valid_long_term).lower(),
            session_id_version=self.caps.session_id_version
        )

    def _login(self) -> Response | None:
        path = "/ISAPI/Security/sessionLogin"

        params = {
            'timeStamp': int(time.time())
        }

        login_data = self.get_login_data()
        login_headers = {
            'Content-Type': 'application/xml'
        }

        response = self.session.post(self.url(path), params=params, data=login_data, headers=login_headers)

        if response.status_code == 200:
            return response
        else:
            response.raise_for_status()

    def get_web_session_and_tag(self) -> dict:
        response = self._login()
        login_root = ET.fromstring(response.content)
        namespace_login = {'ns': login_root.tag.split('}')[0].strip('{')}

        session_tag = login_root.findtext('.//ns:sessionTag', namespaces=namespace_login)
        set_cookie = response.headers.get('Set-Cookie')
        web_session = None
        cookie_parts = set_cookie.split(';')
        for part in cookie_parts:
            if part.startswith('WebSession'):
                web_session = part
                break
        return {
            'Cookie': web_session,
            'Sessiontag': session_tag
        }

    def get_token(self):
        path = '/ISAPI/Security/token'
        params = {'format': 'json'}
        headers = self.get_web_session_and_tag()
        response = self.session.get(self.url(path), params=params, headers=headers)
        if response.status_code == 200:
            return response.json()['Token']['value']
        else:
            response.raise_for_status()

    async def request(
            self, method, path: str, *, params=None, data=None, json=None, headers=None, timeout=None, **kwargs
    ) -> ResponseWrapper:
        async with aiohttp.ClientSession(middlewares=(self.digest_auth,)) as session:
            response = await session.request(
                method, self.url(path), params=params, data=data, json=json, headers=headers, timeout=timeout, **kwargs
            )

            match response.status:
                case 200:
                    response_wrapper = ResponseWrapper(response)
                    if response.content_type == 'application/json':
                        try:
                            response_wrapper.json = await response.json()
                        except UnicodeDecodeError:
                            raw = await response.read()
                            try:
                                response_wrapper.json = jsonlib.loads(raw.decode("utf-8"))
                            except UnicodeDecodeError:
                                response_wrapper.json = jsonlib.loads(raw.decode("gbk", errors="ignore"))
                    if response.content_type == 'image/jpeg':
                        response_wrapper.content = await response.read()
                    return response_wrapper
                case 401:
                    raise ValidationError(_("Wrong username or password."))
                case 400:
                    if response.content_type == 'application/json' and (response_json := await response.json()):
                        raise ValidationError(response_json.get('subStatusCode'))
                    print(await response.text())
            raise response.raise_for_status()
