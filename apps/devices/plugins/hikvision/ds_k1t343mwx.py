from devices.plugins import PluginMixin
from devices.plugins.hikvision import DS_K1T671MF


class DS_K1T343MWX(DS_K1T671MF):
    device_model = PluginMixin.DeviceModels.DS_K1T343MWX
