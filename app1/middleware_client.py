import requests

MIDDLEWARE_URL = 'http://127.0.0.1:5000'

def check_face(timeout=10):
    try:
        response = requests.get(f'{MIDDLEWARE_URL}/check_face', params={'timeout': timeout})
        response.raise_for_status()
        return response.json().get('face_result')
    except requests.RequestException as e:
        print(f"Error checking face: {e}")
        return 'error'


def switch_cam(onoff: bool):
    try:
        response = requests.post(f'{MIDDLEWARE_URL}/switch_cam', json={'on': onoff})
        response.raise_for_status()
        return response.json().get('message')
    except requests.RequestException as e:
        print(f"Error switching camera: {e}")
        return 'error'


def create_user(id_, name, photo):
    try:
        files = {'photo': photo}
        data = {'id_': id_, 'name': name}
        response = requests.post(f'{MIDDLEWARE_URL}/create_user', data=data, files=files)
        response.raise_for_status()
        return response.json().get('status')
    except requests.RequestException as e:
        print(f"Error creating user: {e}")
        return 'failed'


def delete_user(ids):
    try:
        response = requests.delete(f'{MIDDLEWARE_URL}/delete_user', json={'ids': ids})
        response.raise_for_status()
        return response.json().get('status')
    except requests.RequestException as e:
        print(f"Error deleting user: {e}")
        return 'error'


def get_token():
    try:
        response = requests.get(f'{MIDDLEWARE_URL}/get_token')
        response.raise_for_status()
        return response.json().get('token')
    except requests.RequestException as e:
        print(f"Error getting token: {e}")
        return None
