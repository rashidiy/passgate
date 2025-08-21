from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as RestValidationError

from devices.models import Device


class DeviceSerializer(serializers.ModelSerializer):
    immutable_fields = 'ip_address', 'port'
    password = serializers.CharField(source='password_placeholder')

    def validate(self, data):
        if self.instance:
            errors = {}
            for field in self.immutable_fields:
                if field in data:
                    old = getattr(self.instance, field)
                    new = data[field]
                    if new != old:
                        errors[field] = "This field is immutable. Delete the object and recreate it with a new value."
            if errors:
                raise serializers.ValidationError(errors)

        try:
            if self.instance:
                for field in data:
                    if getattr(self.instance, field):
                        setattr(self.instance, field, data[field])
                self.instance.clean()
            else:
                Device(**data).clean()
        except ConnectionError:
            raise RestValidationError('Unable to connect to device')
        except ValidationError as e:
            raise RestValidationError(*e)
        data['encrypted_password'] = data['password_placeholder']
        data['password_placeholder'] = data['password_placeholder'][:1] + '*' * (len(data['password_placeholder']) - 1)
        return super().validate(data)

    class Meta:
        model = Device
        exclude = ['password_placeholder', 'encrypted_password']
