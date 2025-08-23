from rest_framework_nested import routers

from employees.views import EmployeeModelViewSet, CardModelViewSet, AccessPointModelViewSet

router = routers.DefaultRouter()

router.register(r'employee', EmployeeModelViewSet)

nested_router = routers.NestedDefaultRouter(router, r'employee', lookup='employee')
nested_router.register(r'cards', CardModelViewSet, basename='user-cards')
nested_router.register(r'access_points', AccessPointModelViewSet, basename='user-access-points')
urlpatterns = [*router.urls, *nested_router.urls]
