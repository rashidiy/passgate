from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def get_test_webhooks(request: WSGIRequest, *args, **kwargs):
    print(request.body)
    return JsonResponse({'success': True})
