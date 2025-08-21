"""
URL configuration for root project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import logout
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.urls import path, include
from django.views import View

from utils.swagger import schema_view


class LogoutView(View):
    def get(self, request: WSGIRequest, *args, **kwargs):
        next_ = request.GET.get('next')
        logout(request)
        return HttpResponseRedirect(next_)


urlpatterns = [
                  path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                  path('', include("orders.urls")),
                  path('api/v1/users/', include("users.urls")),
                  path('api/v1/devices/', include("devices.urls")),
                  path('accounts/logout/', LogoutView.as_view(), name='logout'),
                  path('', admin.site.urls),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
