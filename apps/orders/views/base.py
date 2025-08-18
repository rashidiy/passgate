from rest_framework.response import Response

from devices.plugins import OrderManager


def get_face_result():
    OrderManager.switch_cam(True)
    face_result = OrderManager.check_face(timeout=10)
    OrderManager.switch_cam(False)
    if face_result == 'unknown':
        error_message = 'Yuz ro\'yxatga olinmagan.'
        return Response({'success': False, 'message': error_message})
    if face_result in ('error', 'timeout'):
        error_message = 'Yuz aniqlanmadi.'
        return Response({'success': False, 'message': error_message})
    return face_result
