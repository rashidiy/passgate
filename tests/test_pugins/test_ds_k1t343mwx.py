import asyncio

import pytest

from devices.plugins import PluginMixin


@pytest.mark.envfile("test_ds_k1t343mwx.env")
@pytest.mark.device(PluginMixin.DeviceModels.DS_K1T343MWX)
class TestDS_K1T343MWX:
    def test__check_model_match(self, plugin):
        assert asyncio.run(plugin._check_model_match()) == (True, PluginMixin.DeviceModels.DS_K1T343MWX)

    def test_create_user(self, plugin, access_point):
        assert asyncio.run(plugin.create_user(access_point))

    def test_update_user(self, plugin, access_point):
        assert asyncio.run(plugin.update_user(access_point))

    def test_add_card(self, plugin, card):
        assert asyncio.run(plugin.add_card(card))

    def test_remove_card(self, plugin, card):
        assert asyncio.run(plugin.remove_card(card))

    def test_get_acs_events(self, plugin, device):
        assert asyncio.run(plugin.get_acs_events(device))

    def test_delete_user(self, plugin, access_point):
        assert asyncio.run(plugin.delete_user(access_point))
