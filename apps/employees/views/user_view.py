from rest_framework import viewsets, parsers

from employees.models import Employee
from employees.serializers import EmployeeCreateSerializer, EmployeeUpdateSerializer


class EmployeeModelViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    swagger_tags = ['Employees']
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        return EmployeeUpdateSerializer
