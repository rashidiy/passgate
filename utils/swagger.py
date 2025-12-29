from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Passgate API",
        default_version='v1',
        description="Documentation for integrated usage of Passgate",
        terms_of_service='None',
        contact=openapi.Contact(name='Telegram', url='https://t.me/samyy_soft_support'),
        license=openapi.License(name='Copyright "OOO Samyy Soft"'),
    ),
    public=True,
    url='http://localhost:8000',
    permission_classes=(permissions.IsAuthenticatedOrReadOnly,),
)


class TaggedAutoSchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys=None):
        view_tags = getattr(self.view, "swagger_tags", None)
        if view_tags:
            return view_tags
        return super().get_tags(operation_keys)
