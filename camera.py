import json
import os
from datetime import datetime
from dotenv import load_dotenv
import urllib3
import hashlib
import requests
import xml.etree.ElementTree as ET
import time
from requests import Response
from requests.auth import HTTPDigestAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()


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


class WebLogin:
    HOST = "http://" + os.getenv("CAM_IP")
    session = requests.Session()

    @classmethod
    def get_capabilities(cls, username) -> Capabilities:
        url = f"{cls.HOST}/ISAPI/Security/sessionLogin/capabilities"
        response = cls.session.get(url, params={'username': username})
        if response.status_code == 200:
            return Capabilities(response)
        else:
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

    @staticmethod
    def get_login_payload(username, enpass, session_id, is_session_id_valid_long_term, session_id_version):
        return f"""
        <SessionLogin>
            <userName>{username}</userName>
            <password>{enpass}</password>
            <sessionID>{session_id}</sessionID>
            <isSessionIDValidLongTerm>{str(is_session_id_valid_long_term).lower()}</isSessionIDValidLongTerm>
            <sessionIDVersion>{session_id_version}</sessionIDVersion>
            <isNeedSessionTag>true</isNeedSessionTag>
        </SessionLogin>
        """

    @classmethod
    def _login(cls, username, password) -> Response:
        url = f"{cls.HOST}/ISAPI/Security/sessionLogin"
        caps = cls.get_capabilities(username)
        encoded_password = cls.encode_password(
            password, caps.challenge, username, caps.salt,
            caps.iterations, caps.is_irreversible
        )

        login_payload = cls.get_login_payload(
            username, encoded_password, caps.session_id,
            caps.is_session_id_valid_long_term, caps.session_id_version
        )

        login_headers = {
            'Content-Type': 'application/xml'
        }
        response = cls.session.post(
            f"{url}?timeStamp={int(time.time())}", data=login_payload, headers=login_headers
        )
        if response.status_code == 200:
            return response
        else:
            response.raise_for_status()

    @classmethod
    def web_session_and_tag(cls, username, password) -> dict:
        response = cls._login(username, password)
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
            'Set-Cookie': web_session,
            'Session-Tag': session_tag
        }

    @classmethod
    def user_set_photo(cls, employee_id, image_path, cookie, sessiontag):
        url = f"http://{os.getenv('CAM_IP')}/ISAPI/Intelligent/FDLib/FDSetUp?format=json"
        headers = {
            "Cookie": cookie,
            "sessiontag": sessiontag
        }
        files = [
            ('img', ('image.png', open(image_path, 'rb'), 'image/png'))
        ]
        data = {
            'FaceDataRecord': '{"faceLibType":"blackFD","FDID":"1","FPID":"%s"}' % employee_id
        }
        response = requests.request("PUT", url, headers=headers, data=data, files=files)
        return response


def switch_cam(onoff: bool):
    json_ = {
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

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Connection": "keep-alive",
        "Origin": f"https://{os.getenv('CAM_IP')}",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }

    response = requests.put(
        f"https://{os.getenv('CAM_IP')}/ISAPI/AccessControl/CardReaderCfg/1?format=json",
        json=json_,
        auth=HTTPDigestAuth(os.getenv('CAM_USER'), os.getenv('CAM_PASS')),
        headers=headers,
        verify=False
    )


def check_face(timeout=10):
    url = f"http://{os.getenv('CAM_IP')}/ISAPI/Event/notification/alertStream"

    try:
        with requests.get(url, auth=HTTPDigestAuth(os.getenv("CAM_USER"), os.getenv("CAM_PASS")),
                          stream=True, timeout=timeout) as response:
            if response.status_code == 200:
                buffer = ""
                # start_time = time.time()
                # if time.time() - start_time > timeout:
                #     return 'timeout'
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("--MIME_boundary") or decoded_line.startswith(
                                "Content-Type") or decoded_line.startswith("Content-Length"):
                            continue
                        buffer += decoded_line.strip()
                        if buffer.count('{') == buffer.count('}'):
                            try:
                                event_data = json.loads(buffer)["AccessControllerEvent"]
                                print(event_data)

                                if event_data["currentVerifyMode"] == "face":
                                    if event_data.get("name"):
                                        return event_data["employeeNoString"]
                                    else:
                                        return 'unknown'
                                buffer = ""
                            except json.JSONDecodeError:
                                return "error"
            else:
                return "error"
    except Exception:
        return 'error'


def get_token():
    token_url = f"https://{os.getenv('CAM_IP')}/ISAPI/Security/token?format=json"

    log_in = WebLogin.web_session_and_tag(os.getenv('CAM_USER'), os.getenv('CAM_PASS'))

    headers = {
        "Accept": "*/*",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": log_in['Set-Cookie'],
        "Sessiontag": log_in['Session-Tag'],
    }

    response = requests.get(
        token_url,
        headers=headers,
        auth=HTTPDigestAuth(os.getenv("CAM_USER"), os.getenv("CAM_PASS")),
        verify=False  # Disable SSL verification
    )
    return json.loads(response.text)['Token']['value']


def create_user(id_, name, photo):
    add_person_url = f"http://{os.getenv('CAM_IP')}/ISAPI/AccessControl/UserInfo/Record?format=json"

    payload = {
        "UserInfo": {
            "employeeNo": str(id_),
            "name": name,
            "userType": "normal",
            "Valid": {
                "enable": True,
                "beginTime": datetime.now().strftime('%Y-%m-%dT00:00:00'),
                "endTime": datetime.now().replace(year=datetime.now().year + 10).strftime("%Y-%m-%dT23:59:59"),
                "timeType": "local"
            },
            "RightPlan": [
                {"doorNo": 1, "planTemplateNo": "1"}
            ],
            "doorRight": "1",
            "groupId": 1,
            "groupName": "Company",
            "localUIRight": False,
            "userLevel": "Employee",
        }
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Connection": "keep-alive",
        "Origin": f"https://{os.getenv('CAM_IP')}",  # Replace with actual origin if different
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }

    response = requests.post(
        add_person_url,
        json=payload,
        headers=headers,
        auth=HTTPDigestAuth(os.getenv("CAM_USER"), os.getenv("CAM_PASS"))
    )

    if response.status_code == 200:
        cookie, session_tag = WebLogin.web_session_and_tag(os.getenv("CAM_USER"), os.getenv("CAM_PASS")).values()
        WebLogin.user_set_photo(id_, photo.path, cookie, session_tag)
        return "added"
    else:
        return "failed"


def delete_user(ids):
    delete_user_url = f"https://{os.getenv('CAM_IP')}/ISAPI/AccessControl/UserInfo/Delete?format=json"

    log_in = WebLogin.web_session_and_tag(os.getenv('CAM_USER'), os.getenv('CAM_PASS'))

    headers = {
        "Accept": "*/*",
        "Cache-Control": "max-age=0",

        "Connection": "keep-alive",
        "Cookie": log_in['Set-Cookie'],
        "Sessiontag": log_in['Session-Tag'],
    }

    payload = {
        "UserInfoDelCond": {
            "EmployeeNoList":
                [{"employeeNo": f"{id_}"} for id_ in ids]
        }
    }

    response = requests.put(
        delete_user_url,
        headers=headers,
        json=payload,
        auth=HTTPDigestAuth(os.getenv("CAM_USER"), os.getenv("CAM_PASS")),
        verify=False,
    )

    if response.status_code == 200:
        return "deleted"
    return "error"
