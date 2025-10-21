from django.db import models


class PluginMixin:
    model = None

    class DeviceModels(models.TextChoices):
        DS_K1T671MF = 'ds_k1t671mf', 'DS-K1T671MF'
        DS_K1T343MWX = 'ds_k1t343mwx', 'DS-K1T343MWX'

    @property
    def plugin(self):
        if self.model is None:
            raise NotImplementedError('PluginMixin requires attribute "model"')
        from devices.plugins.hikvision import DS_K1T671MF, DS_K1T343MWX
        match self.model:
            case self.DeviceModels.DS_K1T671MF:
                return DS_K1T671MF
            case self.DeviceModels.DS_K1T343MWX:
                return DS_K1T343MWX
            case _:
                raise ValueError('Unknown device model.')
