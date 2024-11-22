import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPDigestAuth
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()


def switch_cam(onoff: bool):
    json = {
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
        json=json,
        auth=HTTPDigestAuth(os.getenv('CAM_USER'), os.getenv('CAM_PASS')),
        headers=headers,
        verify=False
    )
