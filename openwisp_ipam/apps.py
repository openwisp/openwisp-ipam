from openwisp_utils.api.apps import ApiAppConfig
from openwisp_utils.utils import default_or_test, register_menu_items
from swapper import get_model_name

from .compat import patch_ipaddress_lib


class OpenWispIpamConfig(ApiAppConfig):
    name = 'openwisp_ipam'
    verbose_name = 'IPAM'

    API_ENABLED = True
    REST_FRAMEWORK_SETTINGS = {
        'DEFAULT_THROTTLE_RATES': {'ipam': default_or_test('400/hour', None)},
    }

    def ready(self, *args, **kwargs):
        super().ready(*args, **kwargs)
        patch_ipaddress_lib()
        items = [
            {'model': get_model_name('openwisp_ipam', 'Subnet')},
            {'model': get_model_name('openwisp_ipam', 'IpAddress')},
        ]
        register_menu_items(items, name_menu='OPENWISP_DEFAULT_ADMIN_MENU_ITEMS')
