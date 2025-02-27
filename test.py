import json
import os
import time
from time import sleep

import requests
from dotenv import load_dotenv
from requests import Response
from requests.auth import HTTPDigestAuth

load_dotenv()




if __name__ == "__main__":
    employee_no = check_face()
    print(employee_no)
