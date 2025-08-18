from rest_framework.response import Response

from orders.plugins.DS_K1T671MF.camera import switch_cam, check_face


def get_face_result():
    switch_cam(True)
    face_result = check_face(timeout=10)
    switch_cam(False)
    if face_result == 'unknown':
        error_message = 'Yuz ro\'yxatga olinmagan.'
        return Response({'success': False, 'message': error_message})
    if face_result in ('error', 'timeout'):
        error_message = 'Yuz aniqlanmadi.'
        return Response({'success': False, 'message': error_message})
    return face_result
