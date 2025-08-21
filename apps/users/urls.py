from rest_framework_nested import routers

from users.views import UserModelViewSet, CardModelViewSet, AccessPointModelViewSet

router = routers.DefaultRouter()

router.register(r'user', UserModelViewSet)

nested_router = routers.NestedDefaultRouter(router, r'user', lookup='user')
nested_router.register(r'cards', CardModelViewSet, basename='user-cards')
nested_router.register(r'access_points', AccessPointModelViewSet, basename='user-access-points')
urlpatterns = [*router.urls, *nested_router.urls]
