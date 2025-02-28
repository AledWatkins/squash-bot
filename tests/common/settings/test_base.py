from common.settings import base


class TestSettings:
    def test_localdev_settings_are_loaded(self):
        assert base.settings
