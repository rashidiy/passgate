import pathlib

import pytest
from dotenv import dotenv_values

from devices.models import Device
from devices.plugins.hikvision import DS_K1T671MF, DS_K1T343MWX
from employees.models import Card, AccessPoint, Employee


def _env_dict(request) -> dict[str, str]:
    test_file = pathlib.Path(str(request.fspath))
    marker = request.node.get_closest_marker("envfile")
    env_path = (test_file.parent / marker.args[0]).resolve() if marker and marker.args else test_file.with_suffix(
        ".env")
    return dotenv_values(env_path) if env_path.exists() else {}


@pytest.fixture
def env(request):
    data = _env_dict(request)

    def get(name, default=None, cast=str):
        val = data.get(name)
        if not val:
            if default is not None:
                return default
            raise ValueError(f'Missing environment variable "{name}"')
        return cast(val)

    return get


@pytest.fixture
def plugin(request, env):
    device_model = request.node.get_closest_marker("device")
    match device_model.args[0]:
        case Device.DeviceModels.DS_K1T671MF:
            p = DS_K1T671MF
        case Device.DeviceModels.DS_K1T343MWX:
            p = DS_K1T343MWX
        case _:
            raise RuntimeError('Unknown device model.')
    return p(env('DEVICE_IP'), env('DEVICE_PORT'), env('DEVICE_USER'), env('DEVICE_PASS'))


@pytest.fixture
def device(env):
    return Device(
        pk=777, name='TestDevice', type=Device.DeviceTypes.ORDER, ip_address=env('DEVICE_IP'),
        port=env('DEVICE_PORT'), username=env('DEVICE_USER'), password_placeholder=env('DEVICE_PASS')
    )


@pytest.fixture
def employee():
    return Employee(pk=777, name='TestEmployee', gender=Employee.Genders.MALE, image='users/test_employee.jpg')


@pytest.fixture
def access_point(device, employee):
    return AccessPoint(
        pk=777,
        employee=employee,
        device=device,
        type=AccessPoint.AccessTypes.NORMAL,
    )


@pytest.fixture
def card(employee):
    return Card(card_no='123', employee=employee)
