from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from app1.views import OrderFoodView

urlpatterns = [
    path("", OrderFoodView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
