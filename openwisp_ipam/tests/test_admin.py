import swapper
from django.test import TestCase

from django_ipam.tests.base.test_admin import BaseTestAdmin


class TestAdmin(BaseTestAdmin, TestCase):
    app_name = 'openwisp_ipam'
    ipaddress_model = swapper.load_model('openwisp_ipam', 'IPAddress')
    subnet_model = swapper.load_model('openwisp_ipam', 'Subnet')
