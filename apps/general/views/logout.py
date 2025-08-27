from django.contrib.auth import logout
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.views import View


class LogoutView(View):
    def get(self, request: WSGIRequest, *args, **kwargs):
        next_ = request.GET.get('next')
        logout(request)
        return HttpResponseRedirect(next_)
