from rest_framework import serializers

from employees.models import Employee


class EmployeeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'gender', 'image']


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)

    class Meta:
        model = Employee
        fields = ['id', 'name', 'gender', 'image']
